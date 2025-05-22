import json
import boto3
import os
from datetime import datetime
from decimal import Decimal
import traceback

# Inicializar clientes de AWS
print("Inicializando clientes de AWS...")
dynamodb = boto3.resource('dynamodb')
sns = boto3.client('sns')

# Obtener el ARN del tema SNS desde las variables de entorno
print("Obteniendo variables de entorno...")
SNS_TOPIC_ARN = os.environ.get('SNS_TOPIC_ARN')
TABLE_NAME = os.environ.get('DYNAMODB_TABLE')
print(f"SNS_TOPIC_ARN: {SNS_TOPIC_ARN}")
print(f"TABLE_NAME: {TABLE_NAME}")

table = dynamodb.Table(TABLE_NAME) if TABLE_NAME else None

class DecimalEncoder(json.JSONEncoder):
    """Clase auxiliar para manejar Decimal en la serialización JSON"""
    def default(self, o):
        if isinstance(o, Decimal):
            return float(o)
        return super(DecimalEncoder, self).default(o)

def check_reservation_conflicts(room_number, check_in_date, check_out_date, current_reservation_id):
    """Verifica conflictos con otras reservas"""
    print(f"\n=== VERIFICANDO CONFLICTOS ===")
    print(f"Habitación: {room_number}")
    print(f"Check-in: {check_in_date}")
    print(f"Check-out: {check_out_date}")
    print(f"ID de reserva actual: {current_reservation_id}")
    
    try:
        # Convertir fechas para comparación
        check_in = datetime.strptime(check_in_date, '%Y-%m-%d')
        check_out = datetime.strptime(check_out_date, '%Y-%m-%d')
        
        # Scan para encontrar reservas en la misma habitación
        filter_expression = "RoomNumber = :room AND ReservationID <> :rid AND #status <> :canceled"
        response = table.scan(
            FilterExpression=filter_expression,
            ExpressionAttributeValues={
                ':room': room_number,
                ':rid': current_reservation_id,
                ':canceled': 'Cancelada'
            },
            ExpressionAttributeNames={
                '#status': 'Status'
            }
        )
        
        print(f"Encontradas {len(response.get('Items', []))} reservas para verificar")
        
        # Verificar solapamientos
        conflicts = []
        for item in response.get('Items', []):
            existing_check_in = datetime.strptime(item['CheckInDate'], '%Y-%m-%d')
            existing_check_out = datetime.strptime(item['CheckOutDate'], '%Y-%m-%d')
            
            if check_in < existing_check_out and check_out > existing_check_in:
                print(f"¡CONFLICTO! con reserva {item['ReservationID']}")
                conflicts.append(item)
        
        print(f"Total de conflictos encontrados: {len(conflicts)}")
        return conflicts
    
    except Exception as e:
        print(f"ERROR en check_reservation_conflicts: {str(e)}")
        print(traceback.format_exc())
        return []

def send_conflict_notification(reservation, conflicts):
    """Envía notificación SNS sobre conflictos"""
    print(f"\n=== ENVIANDO NOTIFICACIÓN DE CONFLICTO ===")
    
    if not SNS_TOPIC_ARN:
        print("ERROR: No se ha configurado SNS_TOPIC_ARN")
        return False
    
    try:
        # Crear mensaje
        subject = f"¡ALERTA! Conflicto de reservas para la habitación {reservation['RoomNumber']}"
        
        message_body = f"""
        Se ha detectado un conflicto de reservas en el sistema del Hotel Cloud Suites.
        
        Detalles de la nueva reserva:
        - ID: {reservation['ReservationID']}
        - Habitación: {reservation['RoomNumber']}
        - Huésped: {reservation.get('GuestName', 'No disponible')}
        - Fecha de entrada: {reservation['CheckInDate']}
        - Fecha de salida: {reservation['CheckOutDate']}
        - Email: {reservation.get('ContactEmail', 'No disponible')}
        
        Esta reserva tiene conflicto con las siguientes reservas existentes:
        """
        
        for conflict in conflicts:
            message_body += f"""
        * Reserva ID: {conflict['ReservationID']}
          - Huésped: {conflict.get('GuestName', 'No disponible')}
          - Fecha de entrada: {conflict['CheckInDate']}
          - Fecha de salida: {conflict['CheckOutDate']}
          - Email: {conflict.get('ContactEmail', 'No disponible')}
        """
        
        message_body += """
        Por favor, contacte a los huéspedes para resolver este conflicto lo antes posible.
        
        Este es un mensaje automático del sistema de reservas del Hotel Cloud Suites.
        """
        
        # Enviar notificación
        print(f"Enviando a SNS Topic: {SNS_TOPIC_ARN}")
        response = sns.publish(
            TopicArn=SNS_TOPIC_ARN,
            Subject=subject,
            Message=message_body
        )
        print(f"Notificación enviada con éxito: {response['MessageId']}")
        return True
    
    except Exception as e:
        print(f"ERROR al enviar notificación SNS: {str(e)}")
        print(traceback.format_exc())
        return False

def update_reservation_status(reservation_id, new_status):
    """Actualiza el estado de una reserva en DynamoDB"""
    print(f"\n=== ACTUALIZANDO ESTADO DE RESERVA ===")
    print(f"ID: {reservation_id}, Nuevo estado: {new_status}")
    
    try:
        updated_at = datetime.now().isoformat()
        
        response = table.update_item(
            Key={'ReservationID': reservation_id},
            UpdateExpression="SET #status = :s, UpdatedAt = :u",
            ExpressionAttributeNames={'#status': 'Status'},
            ExpressionAttributeValues={
                ':s': new_status,
                ':u': updated_at
            },
            ReturnValues="UPDATED_NEW"
        )
        print(f"Actualización exitosa: {response.get('Attributes')}")
        return True
    
    except Exception as e:
        print(f"ERROR al actualizar reserva: {str(e)}")
        print(traceback.format_exc())
        return False

def process_dynamodb_stream_event(record):
    """Procesa un evento de DynamoDB Stream"""
    print("\n=== PROCESANDO EVENTO DYNAMODB STREAM ===")
    
    try:
        # Solo procesamos eventos INSERT o MODIFY
        if record['eventName'] not in ['INSERT', 'MODIFY']:
            print(f"Ignorando evento {record['eventName']}")
            return None
        
        # Extraer los datos de la imagen nueva - CORREGIDO: acceso a través de dynamodb
        if 'dynamodb' not in record or 'NewImage' not in record['dynamodb']:
            print("No hay NewImage en el registro")
            return None
        
        # Convertir de formato DynamoDB a diccionario Python
        reservation = {}
        for key, value in record['dynamodb']['NewImage'].items():
            # Manejar los diferentes tipos de datos de DynamoDB
            if 'S' in value:
                reservation[key] = value['S']
            elif 'N' in value:
                reservation[key] = Decimal(value['N'])
            elif 'BOOL' in value:
                reservation[key] = value['BOOL']
            elif 'NULL' in value:  # AÑADIDO: manejo de valores NULL
                reservation[key] = None
            elif 'M' in value:
                # Mapa (diccionario)
                inner_map = {}
                for inner_key, inner_value in value['M'].items():
                    if 'S' in inner_value:
                        inner_map[inner_key] = inner_value['S']
                    elif 'N' in inner_value:
                        inner_map[inner_key] = Decimal(inner_value['N'])
                    elif 'NULL' in inner_value:  # AÑADIDO: manejo de valores NULL en mapas
                        inner_map[inner_key] = None
                reservation[key] = inner_map
        
        print(f"Reserva extraída del stream: {json.dumps(reservation, cls=DecimalEncoder)}")
        return reservation
    
    except Exception as e:
        print(f"ERROR al procesar evento DynamoDB Stream: {str(e)}")
        print(traceback.format_exc())
        return None

def lambda_handler(event, context):
    """Función principal de la Lambda"""
    print("\n========== INICIO DE EJECUCIÓN ==========")
    print(f"Evento recibido: {json.dumps(event, cls=DecimalEncoder)}")
    
    try:
        # Procesar cada registro del stream
        for record in event.get('Records', []):
            print(f"Procesando registro: {json.dumps(record, cls=DecimalEncoder)}")
            
            # Extraer datos de reserva del evento de stream
            reservation = process_dynamodb_stream_event(record)
            
            # Validar que se obtuvo información válida
            if not reservation or 'ReservationID' not in reservation:
                print("ERROR: No se pudo extraer información válida de reserva")
                continue
            
            # Solo procesar reservas con estado "Pendiente"
            if reservation.get('Status') != 'Pendiente':
                print(f"⚠️ Reserva con estado '{reservation.get('Status')}'. Solo se procesan reservas pendientes.")
                continue
            
            # Verificar campos necesarios
            required_fields = ['RoomNumber', 'CheckInDate', 'CheckOutDate']
            missing_fields = [field for field in required_fields if field not in reservation]
            if missing_fields:
                print(f"ERROR: Faltan campos necesarios en la reserva: {missing_fields}")
                continue
            
            # Verificar si hay conflictos
            conflicts = check_reservation_conflicts(
                reservation['RoomNumber'],
                reservation['CheckInDate'],
                reservation['CheckOutDate'],
                reservation['ReservationID']
            )
            
            # Procesar según resultado de la verificación
            if conflicts:
                print(f"Se encontraron {len(conflicts)} conflictos")
                # Marcar reserva como conflictiva
                update_success = update_reservation_status(reservation['ReservationID'], 'Conflicto')
                if not update_success:
                    print("ADVERTENCIA: No se pudo actualizar el estado a 'Conflicto'")
                
                # Enviar notificación
                notification_sent = send_conflict_notification(reservation, conflicts)
                if not notification_sent:
                    print("ADVERTENCIA: No se pudo enviar la notificación de conflicto")
                else:
                    print("Notificación de conflicto enviada correctamente")
            else:
                print("No se encontraron conflictos")
                # Si es pendiente, marcarla como confirmada
                if reservation.get('Status') == 'Pendiente':
                    update_success = update_reservation_status(reservation['ReservationID'], 'Confirmada')
                    if update_success:
                        print("Reserva marcada como 'Confirmada' exitosamente")
                    else:
                        print("ADVERTENCIA: No se pudo actualizar el estado a 'Confirmada'")
        
        print("========== FIN DE EJECUCIÓN ==========")
        return {
            'statusCode': 200,
            'body': json.dumps('Procesamiento completado con éxito')
        }
    
    except Exception as e:
        print(f"ERROR CRÍTICO: {str(e)}")
        print(traceback.format_exc())
        return {
            'statusCode': 500,
            'body': json.dumps(f'Error en el procesamiento: {str(e)}')
        }
