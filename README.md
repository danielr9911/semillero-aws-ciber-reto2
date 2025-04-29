
# Reto 2: Despliegue de recursos a través de CloudFormation


## 1. Contexto y objetivo


Para la ejecución de los 3 retos de la Fase 1 del Semillero AWS Ciber🚀supondremos el mismo escenario base que utilizamos en el Reto 1. Sin embargo, en esta ocasión, daremos un paso adelante en la implementación de buenas prácticas mediante la Infraestructura como Código (IaC).


### Objetivo general: 
- Desarrollar las competencias fundamentales en AWS de manera práctica, desde el nivel principiante hasta un nivel práctico intermedio, capacitando a los participantes para diseñar, implementar y mantener arquitecturas seguras y eficientes en la nube que cumplan con los estándares y políticas de la organización, preparándolos así para contribuir efectivamente en iniciativas de transformación digital y proyectos de migración dentro de la organización.


### Objetivo específico del Reto 2: 
- Aprender a utilizar AWS CloudFormation para implementar Infraestructura como Código (IaC) 
- Desarrollar un template YAML de CloudFormation para automatizar el despliegue de una arquitectura completa 
- Comprender las ventajas de la automatización para garantizar entornos repetibles, consistentes y auditables 
- Profundizar en la gestión de recursos AWS a través de código declarativo


## 2. Arquitectura escenario base


El Hotel "Cloud Suites" necesita implementar un sistema de gestión de reservas en la nube para optimizar sus operaciones y mejorar la experiencia de sus clientes. Como especialista en AWS, has sido contratado para diseñar e implementar esta solución utilizando diversos servicios de la nube de Amazon.


Se desea desarrollar un sistema de reservas que permita crear, modificar, eliminar y visualizar reservas de habitaciones, validar disponibilidad y notificar cuando existan conflictos en las reservaciones.


El sistema constará de los siguientes componentes de AWS:
![Arquitectura de la solución](diagrama-arquitectura-reto1-semillero.jpg)

- **VPC (Virtual Private Cloud)**  
 La VPC es un recurso de red y permite controlar la conectividad y la seguridad. Se tendrá una Subnet privada donde estarán los recursos sensibles y una Subnet pública que se podrá alcanzar desde Internet.

- **EC2 (Elastic Cloud Computing)**  
 Una instancia EC2 es un recurso de cómputo (servidor) y permitirá alojar la aplicación web desarrollada en Python con el framework Flask para la interfaz de usuario.  
 *Nota: No tendrás que desarrollar la lógica del servidor web. Adjunto al reto encontrarás el archivo app.py. También en la guía se entrega el paso a paso de los comandos Linux para su despliegue.*

- **Bucket S3 (Simple Storage Service)**  
 Un Bucket de S3 es un recurso que permite almacenar archivos en la nube (documentos, imágenes, videos, etc.). Guardará archivos estáticos de la aplicación web y documentos de identidad de los huéspedes.

- **Lambda en Python**  
 Una función Lambda es un recurso de cómputo de tipo "Serverless" o "Sin servidor", que permite ejecutar código fuente sin necesidad de administrar servidores. Validará las nuevas reservas para detectar conflictos (misma habitación y fechas).  
 *Nota: No tendrás que desarrollar la lógica en Pyhton. Adjunto al reto encontrarás el archivo lambda_function.py.*

- **DynamoDB**  
 Una DyanmoDB es una base de datos no relacional (NoSQL) que almacenará la información de las reservas y habitaciones.

- **Amazon CloudWatch Event (EventBridge)**  
 Un evento de EventBridge permite disparar una ejecución basándose en reglas o programación de calendario. Disparará la función Lambda cuando se cree o modifique una reserva en DynamoDB.

- **Amazon SNS (Simple Notification Service)**  
 Un SNS es un servicio que permite realizar notificaciones de manera asíncrona. Enviará notificaciones por correo electrónico al administrador del hotel (tú) cuando se detecten conflictos.

- **IAM Role**  
 Un Rol de IAM es una identidad en AWS que agrupa permisos hacia otros recursos de AWS. Gestionará los permisos necesarios entre los distintos servicios.

- **Servicios de Seguridad y Monitoreo**  
 Estos servicios no hacen parte de la arquitectura base como tal, sin embargo, como miembros del Entorno de Ciberseguridad es importante conocerlos y aprenderlos a utilizar:
 - **AWS IAM**: Configuración de roles y políticas para cada recurso, asegurando el principio de menor privilegio
  - **AWS CloudTrail**: Registra todas las llamadas a la API de AWS realizadas en la cuenta, lo que permite auditar actividades
  - **Amazon CloudWatch**: Se utiliza para almacenar y visualizar logs (por ejemplo, logs de la aplicación web y la función Lambda) y para configurar alarmas
  - **AWS Config**: Se utiliza para realizar evaluaciones de la conformidad de las configuraciones de los recursos desplegados
  - **AWS Security Hub**: Centraliza los hallazgos e incumplimientos encontrados por diferentes herramientas sobre los recursos de la cuenta
 
## 3. Uso responsable de Cuenta AWS Sandbox

La organización cuenta con un conjunto de cuentas independiente a las productivas para que los equipos realicen pruebas de concepto.

Para el desarrollo del Semillero, utilizaremos la cuenta CiberseguridadSBX. Esta cuenta genera una facturación por uso para la organización, por lo que debemos ser muy responsables en la creación de nuevos recursos, limitándonos a los indicados en el reto.

**Enlace para Consola de AWS SBX:**  
https://d-906705dbfe.awsapps.com/start#/

**Nombramiento de recursos:**  
Con el fin de identificar los recursos que han sido creados en el semillero y realizar una posterior depuración de estos al finalizar, seguiremos el siguiente nombramiento de TODOS los recursos que se creen para cada uno de los retos:

```
semillero-[USUARIO]-[NOMBRE-DEL-RECURSO]
```

Ejemplo:
```
semillero-danirend-miprimerbucket
```

# Guía para la implementación con CloudFormation

A continuación, se presenta una guía para implementar la solución utilizando CloudFormation.

> 💡 Si tienes conocimientos previos en AWS y quieres hacerlo por tu cuenta ¡Adelante! Acá tendrás igualmente la guía si tienes alguna duda.

## Paso 1: Creación y estructura del template CloudFormation


Para comenzar, necesitarás crear un archivo YAML que contendrá toda la definición de tu infraestructura. Este archivo tendrá varias secciones fundamentales:


1. AWSTemplateFormatVersion: Versión del formato de plantilla 
2. Description: Descripción sobre lo que hace el template 
3. Parameters: Parámetros que se pueden personalizar al implementar la plantilla 
4. Resources: Recursos de AWS que se crearán 
5. Outputs: Valores de salida que se mostrarán después de crear los recursos


Estructura básica del template:


```yaml 
AWSTemplateFormatVersion: 
2010-09-09
 
Description: 
Sistema de Reservas de Hotel para Semillero AWS Ciber



Parameters: 
Usuario: 
Type: String 
Description: Tu nombre de usuario para la nomenclatura de recursos


Resources: 
# Aquí irán los recursos de AWS


Outputs: 
# Aquí irán los valores de salida 
```


Recursos de ayuda: 
- [Documentación oficial de CloudFormation](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/template-reference.html)
- [Anatomía de una plantilla CloudFormation](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/template-anatomy.html)


## Paso 2: Definición de recursos en CloudFormation

A continuación, deberás definir cada uno de los recursos necesarios para la arquitectura. Para cada recurso, te proveemos el tipo de recurso de CloudFormation y un enlace a la documentación de referencia.

### 2.1 Bucket S3


```yaml 
HotelBucket: 
  Type: AWS::S3::Bucket 
  Properties: 
    BucketName: !Sub "semillero-${Usuario}-hotel-reservations" 
    # Aquí definir las demás propiedades 
```


Documentación: [AWS::S3::Bucket](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-s3-bucket.html)


### 2.2 Tabla DynamoDB


```yaml 
ReservationsTable: 
  Type: AWS::DynamoDB::Table 
  Properties: 
    TableName: !Sub "semillero-${Usuario}-HotelReservations" 
    # Especificar clave primaria, capacidad, etc. 
```


Documentación: [AWS::DynamoDB::Table](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dynamodb-table.html)


### 2.3 Tema SNS


```yaml 
ReservationConflictTopic: 
  Type: AWS::SNS::Topic 
  Properties: 
    TopicName: !Sub "semillero-${Usuario}-HotelReservationConflicts" 
    # Otras propiedades 
```


Documentación: [AWS::SNS::Topic](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-sns-topic.html)


### 2.4 Suscripción SNS


```yaml 
EmailSubscription: 
  Type: AWS::SNS::Subscription 
  Properties: 
    Protocol: email 
    Endpoint: tu-email@ejemplo.com 
    TopicArn: !Ref ReservationConflictTopic 
```


Documentación: [AWS::SNS::Subscription](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-sns-subscription.html)


### 2.5 VPC y Networking


```yaml 
HotelVPC: 
Type: AWS::EC2::VPC 
Properties: 
CidrBlock: 10.0.0.0/16 
# Otras propiedades


PublicSubnet: 
Type: AWS::EC2::Subnet 
Properties: 
VpcId: !Ref HotelVPC 
CidrBlock: 10.0.0.0/24 
# Otras propiedades


PrivateSubnet: 
Type: AWS::EC2::Subnet 
Properties: 
VpcId: !Ref HotelVPC 
CidrBlock: 10.0.1.0/24 
# Otras propiedades


# Definir también: Internet Gateway, Route Tables, NAT Gateway 
```


Documentación: 
- [AWS::EC2::VPC](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-vpc.html) 
- [AWS::EC2::Subnet](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-subnet.html) 
- [AWS::EC2::InternetGateway](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-internetgateway.html)
- [AWS::EC2::RouteTable](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-routetable.html)
- [AWS::EC2::NatGateway](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-natgateway.html)


### 2.6 IAM Roles


```yaml 
LambdaRole: 
Type: AWS::IAM::Role 
Properties: 
RoleName: !Sub "semillero-${Usuario}-LambdaHotelReservationRole" 
AssumeRolePolicyDocument: 
Version: 
2012-10-17
 
Statement: 
- Effect: Allow 
Principal: 
Service: lambda.amazonaws.com 
Action: 
sts:AssumeRole
 
# Definir ManagedPolicyArns o políticas inline


EC2Role: 
Type: AWS::IAM::Role 
Properties: 
RoleName: !Sub "semillero-${Usuario}-EC2HotelReservationRole" 
# Definir políticas de asunción y permisos 
```


Documentación: [AWS::IAM::Role](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iam-role.html)


### 2.7 Función Lambda


```yaml 
ValidateReservationFunction: 
  Type: AWS::Lambda::Function 
  Properties: 
    FunctionName: !Sub "semillero-${Usuario}-ValidateHotelReservation" 
    Runtime: python3.13 
    Handler: lambda_function.lambda_handler 
    Role: !GetAtt LambdaRole.Arn 
    Code: 
      ZipFile: | 
        # Código de la función lambda_function.py aquí 
    Environment: 
      Variables: 
        SNS_TOPIC_ARN: !Ref ReservationConflictTopic 
        DYNAMODB_TABLE: !Ref ReservationsTable 
    # Definir configuración de VPC 
```


Documentación: [AWS::Lambda::Function](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-lambda-function.html)


### 2.8 Regla de EventBridge


```yaml 
ReservationValidatorRule: 
  Type: AWS::Events::Rule 
  Properties: 
    Name: !Sub "semillero-${Usuario}-HotelReservationValidator" 
    Description: "Regla para activar la validación de reservas de hotel" 
    EventPattern: 
      # Definir el patrón de eventos para DynamoDB 
    Targets: 
      - Arn: !GetAtt ValidateReservationFunction.Arn 
        Id: "ValidateReservationTarget" 
```


Documentación: [AWS::Events::Rule](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-events-rule.html)


### 2.9 Grupos de Seguridad


```yaml 
WebServerSecurityGroup: 
Type: AWS::EC2::SecurityGroup 
Properties: 
GroupName: !Sub "semillero-${Usuario}-sg-web-server" 
GroupDescription: "Grupo de seguridad para el servidor web" 
VpcId: !Ref HotelVPC 
SecurityGroupIngress: 
- IpProtocol: tcp 
FromPort: 80 
ToPort: 80 
CidrIp: 0.0.0.0/0 
# Definir otras reglas de ingreso


LambdaSecurityGroup: 
Type: AWS::EC2::SecurityGroup 
Properties: 
GroupName: !Sub "semillero-${Usuario}-sg-lambda" 
# Definir otras propiedades 
```


Documentación: [AWS::EC2::SecurityGroup](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-security-group.html)


### 2.10 Instancia EC2


```yaml 
HotelWebServer: 
  Type: AWS::EC2::Instance 
  Properties: 
    InstanceType: t2.micro 
    ImageId: ami-0f3581... # Especificar AMI ID apropiada para Amazon Linux 2023 
    SubnetId: !Ref PublicSubnet 
    SecurityGroupIds: 
      - !Ref WebServerSecurityGroup 
    IamInstanceProfile: !Ref EC2InstanceProfile 
    UserData: 
      Fn::Base64: !Sub | 
        #!/bin/bash 
        # Script de inicialización del servidor 
    # Otras propiedades 
```


Documentación: [AWS::EC2::Instance](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-instance.html)


## Paso 3: Despliegue del template CloudFormation


Una vez que hayas creado tu template YAML completo, debes desplegarlo a través de la consola de AWS:


1. Acceder a CloudFormation: 
- En la barra de búsqueda superior, escribe "CloudFormation" y selecciona el servicio.


2. Crear un stack: 
- Haz clic en "Crear stack" > "Con nuevos recursos (estándar)". 
- Selecciona "Cargar un archivo de plantilla" y sube tu archivo YAML. 
- Haz clic en "Siguiente".


3. Especificar detalles del stack: 
- Nombre del stack: semillero-[USUARIO]-hotel-system 
- Parámetros: Ingresa tu nombre de usuario y cualquier otro parámetro definido. 
- Haz clic en "Siguiente".


4. Configurar opciones del stack: 
- En la sección de etiquetas, puedes añadir: 
- Key: Project, Value: Semillero - Reto 2 
- Key: Environment, Value: SBX 
- Key: Owner, Value: [USUARIO] 
- Haz clic en "Siguiente".


5. Revisar: 
- Revisa todos los detalles del stack. 
- Marca la casilla de reconocimiento de que CloudFormation podría crear recursos IAM. 
- Haz clic en "Crear stack".


6. Monitorear el progreso: 
- Espera a que el estado del stack cambie a "CREATE_COMPLETE". 
- Si hay errores, revisa la pestaña "Eventos" para identificar el problema.


## Paso 4: Configuración final y pruebas


Una vez que el stack se haya implementado correctamente:


1. Acceder a la instancia EC2: 
- En la consola de EC2, encuentra la instancia creada por CloudFormation. 
- Conéctate a través de Session Manager como en el Reto 1.


2. Configurar la aplicación: 
- Sigue los mismos pasos del Reto 1 para clonar el repositorio y configurar la aplicación. 
- Asegúrate de actualizar las variables específicas en el archivo app.py.


3. Probar el sistema: 
- Accede a la aplicación web a través de la IP pública de la instancia EC2. 
- Realiza pruebas creando reservas y generando conflictos.


# Posibles errores y soluciones


### 1. Error: Resource already exists


Problema: Intento crear un recurso con un nombre que ya existe globalmente (como un bucket S3)


Solución: 
- Cambia el nombre del recurso añadiendo un sufijo numérico único 
- Si estás reintentando después de un despliegue fallido, asegúrate de eliminar cualquier recurso creado previamente


### 2. Error: Template format error


Problema: El formato YAML es incorrecto


Solución: 
- Verifica la indentación (espacios) en tu archivo YAML 
- Usa un validador YAML online para verificar la sintaxis 
- Asegúrate de que no estés mezclando tabulaciones con espacios


### 3. Error: Parameter value <value> is not valid for parameter <name>


Problema: Un parámetro no cumple con las restricciones definidas


Solución: 
- Revisa los requisitos específicos para ese parámetro (longitud, formato) 
- Verifica que estés usando el tipo de valor correcto (string, número, etc.)


### 4. Error: Circular dependency between resources


Problema: Hay una dependencia circular entre los recursos


Solución: 
- Revisa tus referencias usando !Ref o !GetAtt 
- Reorganiza la estructura para eliminar la dependencia circular 
- Usa DependsOn para controlar el orden de creación de recursos


### 5. Error: Not authorized to perform iam:CreateRole


Problema: Permisos insuficientes para crear roles IAM


Solución: 
- Asegúrate de tener los permisos adecuados en tu cuenta 
- Marca la casilla de reconocimiento IAM al crear el stack


### 6. Error: Failed to send notification to topic ARN


Problema: La confirmación del tema SNS no se completó


Solución: 
- Verifica que la dirección de correo electrónico sea válida 
- Confirma la suscripción al SNS después de que se cree el stack


## Estrategia para reintentar después de errores:


1. Revisar detenidamente los eventos en CloudFormation para identificar el error exacto 
2. Eliminar el stack fallido antes de reintentar (Acciones > Eliminar stack) 
3. Corregir el problema en el template YAML 
4. Crear un nuevo stack con el template corregido


# Tareas opcionales adicionales (Puntos extras)


1. Implementar Parámetros y Mapeos en CloudFormation: 
- Añade parámetros adicionales que permitan configurar aspectos como el tamaño de la instancia EC2 
- Usa la sección "Mappings" para definir diferentes configuraciones según la región 
- Implementa validación de parámetros con restricciones y valores permitidos


2. Mejorar la seguridad con Nested Stacks: 
- Divide tu arquitectura en stacks anidados (uno para networking, otro para la aplicación, etc.) 
- Implementa el principio de privilegio mínimo creando stacks específicos para recursos sensibles 
- Documenta cómo los stacks anidados mejoran la seguridad y gobernanza


3. Implementar una infraestructura Multi-AZ: 
- Modifica tu template para desplegar recursos en múltiples zonas de disponibilidad 
- Configura una estrategia de alta disponibilidad para la aplicación 
- Documenta cómo esta arquitectura mejora la resiliencia ante fallos


4. Integración con AWS Secrets Manager: 
- Modifica el template para almacenar contraseñas y claves en AWS Secrets Manager 
- Configura la aplicación para recuperar estos secretos de forma segura 
- Documenta las mejores prácticas implementadas para gestión de secretos


5. Implementar Drift Detection y Stack Policies: 
- Configura la detección de desviaciones (drift) en tu stack de CloudFormation 
- Implementa políticas de stack para proteger recursos críticos contra actualizaciones accidentales 
- Demuestra un caso de uso donde la detección de drift identifica cambios manuales no autorizados


# Sistema de puntuación


La evaluación del Reto 2 se realizará de acuerdo con el siguiente sistema de puntuación:


## Componentes Básicos (80 puntos) 
- Template CloudFormation completo y funcional (50 puntos) 
- Estructura correcta del template (formato, secciones): 5 puntos 
- Recursos de almacenamiento (S3, DynamoDB): 10 puntos 
- Recursos de comunicación (SNS, EventBridge): 10 puntos 
- Recursos de red (VPC, Subnets, Security Groups): 10 puntos 
- Recursos de cómputo (EC2, Lambda): 10 puntos 
- Roles y políticas IAM correctamente definidos: 5 puntos


## Despliegue y funcionamiento (30 puntos) 
- Despliegue exitoso del stack completo: 10 puntos 
- Aplicación web accesible y funcional: 10 puntos 
- Sistema de validación y notificación de conflictos operando correctamente: 10 puntos


## Tareas Adicionales (20 puntos) 
- Implementar Parámetros y Mapeos: 4 puntos 
- Mejorar la seguridad con Nested Stacks: 4 puntos 
- Implementar una infraestructura Multi-AZ: 4 puntos 
- Integración con AWS Secrets Manager: 4 puntos 
- Implementar Drift Detection y Stack Policies: 4 puntos


## Registro de avance en Planner 
Para registrar tu avance y enviar evidencias: 
1. Accede al Planner del equipo en MS Teams (Grupo Semillero AWS Ciber) 
2. Marca cada tarea como completada conforme avances 
3. Adjunta capturas de pantalla como evidencia para cada componente 
4. Cuando hayas finalizado todo el reto, marca la tarea "Reto 2 Completado"


Recuerda que los 5 participantes con mayor puntuación al final del reto obtendrán un reconocimiento. 
¡Buena suerte en la implementación de tu sistema de reservas en la nube usando CloudFormation!


# Guía para la eliminación de recursos


Al finalizar el reto, es importante eliminar todos los recursos creados para evitar costos innecesarios y mantener limpia la cuenta AWS. Cuando usas CloudFormation, la eliminación es más sencilla:


## Eliminar el stack completo de CloudFormation


1. Accede a la consola de CloudFormation 
2. Selecciona tu stack semillero-[USUARIO]-hotel-system 
3. Haz clic en "Eliminar" 
4. Confirma la eliminación


CloudFormation eliminará automáticamente todos los recursos que fueron creados por el stack en el orden correcto.


## Verificación de eliminación completa


1. Espera a que el estado del stack cambie a "DELETE_COMPLETE" 
2. Si hay errores en la eliminación, revisa los eventos para identificar qué recursos no se pudieron eliminar 
3. Para recursos que no se eliminaron automáticamente: 
- Es posible que tengan la protección contra eliminación activada 
- Algunos recursos como buckets S3 con contenido deben vaciarse manualmente antes


## Recursos que podrían requerir limpieza manual


- Buckets S3: Si contienen archivos, debes vaciarlos manualmente 
- Suscripciones SNS: Podrían requerir eliminación manual 
- CloudWatch Logs: Los grupos de logs creados por Lambda o EC2 podrían persistir


## Verificación final


Utiliza la barra de búsqueda global con el prefijo semillero-[USUARIO] para asegurarte de que no queden recursos sin eliminar.


> Importante: La eliminación de estos recursos es definitiva y los datos no se podrán recuperar.
