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

Para comenzar, necesitarás crear un archivo YAML que contendrá toda la definición de tu infraestructura. Este archivo tendrá las siguientes secciones fundamentales:

```yaml
AWSTemplateFormatVersion: '2010-09-09'
Description: 'Sistema de Reservas para Hotel - Infraestructura AWS'

Parameters:
  # Aquí definirás parámetros para personalizar el despliegue

Resources:
  # Aquí definirás todos los recursos AWS que se crearán

Outputs:
  # Aquí definirás información que quieres mostrar después del despliegue
```

### Sección Parameters

Utiliza estos parámetros ya definidos para tu template:

```yaml
Parameters:
  UserName:
    Type: String
    Description: 'Nombre de usuario para prefijo de recursos'
    Default: 'usuario'
  # Ya que utilizaremos una VPC existente, definimos parámetros para los recursos de red
  VpcId:
    Type: AWS::EC2::VPC::Id
    Description: 'ID de la VPC existente donde se desplegarán los recursos'
    Default: 'vpc-052071eb751480a6b'  # ID de la VPC del semillero
  PublicSubnetId:
    Type: AWS::EC2::Subnet::Id
    Description: 'ID de la subnet pública existente para la instancia EC2'
    Default: 'subnet-0ffc2bc5959b5a2ab'  # ID de la subnet pública del semillero
  PrivateSubnetId:
    Type: AWS::EC2::Subnet::Id
    Description: 'ID de la subnet privada existente para la función Lambda'
    Default: 'subnet-0b2ac96840c048166'  # ID de la subnet privada del semillero
```

> 💡 Nota importante: En este reto, NO crearemos una nueva VPC ni subnets. Utilizaremos la infraestructura de red ya existente en la cuenta del semillero para evitar alcanzar los límites de la cuenta. Los IDs ya están incluidos como valores predeterminados.

## Paso 2: Definición de recursos en CloudFormation

A continuación, deberás definir los recursos necesarios para la arquitectura. Para cada recurso te proporcionamos el nombre lógico (Logical ID) y el tipo de recurso que debes usar, pero tendrás que investigar las propiedades necesarias.

### 2.1 Bucket S3

Documentación: [AWS::S3::Bucket](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-s3-bucket.html)

### 2.2 Política de Bucket S3

Documentación: [AWS::S3::BucketPolicy](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-s3-policy.html)

### 2.3 Tabla DynamoDB

Documentación: [AWS::DynamoDB::Table](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dynamodb-table.html)

### 2.4 Tema SNS

Documentación: [AWS::SNS::Topic](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-sns-topic.html)

### 2.5 Suscripción SNS

Documentación: [AWS::SNS::Subscription](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-sns-subscription.html)

### 2.6 Rol de ejecución para Lambda

Documentación: [AWS::IAM::Role](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iam-role.html)

### 2.7 Grupo de seguridad para Lambda

Documentación: [AWS::EC2::SecurityGroup](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-security-group.html)

### 2.8 Función Lambda

> 💡 Pista importante: En la propiedad Code: ZipFile: debes colocar el código Python de la función Lambda (archivo lambda_function.py). Recuerda configurar correctamente el handler para evitar errores de importación.

Documentación: [AWS::Lambda::Function](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-lambda-function.html)

### 2.9 Regla de EventBridge

Documentación: [AWS::Events::Rule](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-events-rule.html)

### 2.10 Permiso para EventBridge

Documentación: [AWS::Lambda::Permission](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-lambda-permission.html)

### 2.11 Rol para instancia EC2

Documentación: [AWS::IAM::Role](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iam-role.html)

### 2.12 Perfil de instancia para EC2

Documentación: [AWS::IAM::InstanceProfile](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iam-instanceprofile.html)

### 2.13 Grupo de seguridad para EC2

Documentación: [AWS::EC2::SecurityGroup](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-security-group.html)

### 2.14 Instancia EC2

> 💡 Pista importante: En la propiedad UserData: Fn::Base64: !Sub | debes colocar las líneas de bash indicadas a continuación. Estos comandos se ejecutarán automáticamente al iniciar la instancia y están diseñados para que suban de manera autonoma la aplicación.

```bash
    #!/bin/bash  
    # Actualizar el sistema e instalar dependencias 
    yum update -y 
    yum install -y python3 python3-pip git 

    # Crear directorio para la aplicación 
    mkdir -p /opt/hotel-app 

    # Clonar el repositorio con la aplicación 
    cd /opt/hotel-app 
    git clone https://github.com/danielr9911/semillero-aws-ciber-reto1.git . 

    # Instalar dependencias de Python 
    pip3 install -r requirements.txt 

    # Crear directorios necesarios para el almacenamiento local 
    mkdir -p local_storage/documents 

    # Modificar app.py para usar los recursos creados por CloudFormation 
    sed -i "s/S3_BUCKET_NAME = 'semillero-\[USUARIO\]-hotel-reservations'/S3_BUCKET_NAME = 'semillero-${UserName}-hotel-reservations'/" app.py 
    sed -i "s/DYNAMODB_TABLE = 'semillero-\[USUARIO\]-HotelReservations'/DYNAMODB_TABLE = 'semillero-${UserName}-HotelReservations'/" app.py 

    # Crear un archivo de servicio systemd 
    cat > /etc/systemd/system/hotel-app.service << 'EOF' 
    [Unit] 
    Description=Hotel Reservation Application 
    After=network.target 

    [Service] 
    User=root 
    WorkingDirectory=/opt/hotel-app 
    ExecStart=/usr/bin/python3 app.py 
    Restart=always 

    [Install] 
    WantedBy=multi-user.target 
    EOF 

    # Habilitar e iniciar el servicio 
    systemctl daemon-reload 
    systemctl enable hotel-app 
    systemctl start hotel-app 
```

Documentación: [AWS::EC2::Instance](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-instance.html)

## Paso 3: Despliegue del template CloudFormation

Una vez que hayas creado tu template YAML completo, debes desplegarlo a través de la consola de AWS:

### 3.1 Acceder a CloudFormation

1. Inicia sesión en la consola AWS con las credenciales del semillero 
2. En la barra de búsqueda superior, escribe "CloudFormation" y selecciona el servicio

### 3.2 Crear un stack

1. Haz clic en "Crear stack" > "Con nuevos recursos (estándar)" 
2. En la sección "Especificar plantilla": 
- Selecciona "Cargar un archivo de plantilla" 
- Haz clic en "Elegir archivo" y selecciona tu template YAML 
- Primera validación: En este punto, CloudFormation realizará una validación sintáctica del template. Si hay errores en la estructura YAML o propiedades inválidas, se mostrará un error. 
- Si la validación es exitosa, haz clic en "Siguiente"

### 3.3 Especificar detalles del stack

1. Nombre del stack: semillero-[USUARIO]-hotel-system (reemplaza [USUARIO] por tu nombre de usuario) 
2. Parámetros: 
- UserName: ingresa tu nombre de usuario para que todos los recursos tengan ese prefijo 
- Los demás parámetros (VpcId, PublicSubnetId, PrivateSubnetId) puedes dejarlos con los valores predeterminados 
3. Haz clic en "Siguiente"

### 3.4 Configurar opciones del stack

1. En la sección de etiquetas, puedes añadir: 
- Key: Project, Value: Semillero - Reto 2 
- Key: Environment, Value: SBX 
- Key: Owner, Value: [USUARIO] 
2. Deja el resto de opciones con sus valores predeterminados 
3. Haz clic en "Siguiente"

### 3.5 Revisar y crear

1. Revisa todos los detalles del stack y los parámetros configurados 
2. MUY IMPORTANTE: En la parte inferior, marca la casilla que dice "Acepto que AWS CloudFormation podría crear recursos de IAM con nombres personalizados" 
3. Haz clic en "Crear stack"

### 3.6 Monitorear el progreso

1. Segunda validación: Durante la creación del stack, CloudFormation validará recursos individuales y sus dependencias 
2. La creación del stack puede tardar varios minutos (hasta 10-15 minutos) 
3. Puedes seguir el progreso en la pestaña "Eventos" 
4. Si todo va bien, el estado del stack cambiará a "CREATE_COMPLETE" 
5. Si hay errores, el estado será "CREATE_FAILED" y deberás revisar la pestaña "Eventos" para identificar el problema

## Paso 4: Prueba de la aplicación

Cuando el stack esté completamente creado:

1. Ve a la pestaña "Salidas" del stack 
2. Localiza la salida "ApplicationURL" 
3. Haz clic en el enlace o cópialo a tu navegador 
4. Deberías ver la interfaz web del sistema de reservas del hotel

## Errores comunes y sus soluciones

### 1. Error: Template format error

Problema: Hay un problema con la sintaxis YAML del template.

Posibles causas y soluciones: 
- Indentación incorrecta: YAML es sensible a la indentación. Usa siempre espacios (no tabulaciones) y mantén una indentación consistente (generalmente 2 o 4 espacios). 
- Falta de comillas: Si tus valores contienen caracteres especiales, enciérralos en comillas. 
- Referencias incorrectas: Verifica que todas las referencias (!Ref, !GetAtt) apunten a recursos existentes.

Herramienta útil: Usa un validador YAML online como YAML Lint para verificar tu archivo antes de subirlo.

### 2. Error: Resource already exists

Problema: Estás intentando crear un recurso con un nombre que ya existe (común con buckets S3 y nombres de roles).

Solución: 
- Modifica el prefijo o agrega un sufijo al nombre del recurso (por ejemplo, un número aleatorio). 
- Si estás reintentando un despliegue fallido, elimina primero todos los recursos residuales.

### 3. Error: Not authorized to perform iam:CreateRole

Problema: No tienes permisos suficientes para crear roles IAM.

Solución: 
- Asegúrate de marcar la casilla de reconocimiento IAM al crear el stack. 
- Verifica con el instructor si tu usuario tiene los permisos necesarios.

### 4. Error: Template contains errors: Invalid template resource property

Problema: Una propiedad configurada incorrectamente en algún recurso.

Solución: 
- Revisa la documentación oficial del recurso específico. 
- Verifica valores permitidos para propiedades como políticas IAM, configuraciones de seguridad, etc.

### 5. Error con Lambda: Unable to import module 'lambda_function'

Problema: El nombre del handler configurado no coincide con el archivo de código.

Solución: 
- Asegúrate de que el handler sea index.lambda_handler si estás usando ZipFile. 
- Verifica que el código Python no tenga errores de sintaxis.

### 6. Error en la aplicación web: La aplicación no responde

Problema: La instancia EC2 no está configurada correctamente o la aplicación no está ejecutándose.

Solución: 
- Conéctate a la instancia mediante Session Manager. 
- Revisa los logs: systemctl status hotel-app o journalctl -u hotel-app. 
- Verifica que el script UserData se ejecutó correctamente: cat /var/log/cloud-init-output.log.

## Estrategia para reintentar después de errores

Si tu despliegue falla, sigue estos pasos para resolverlo:

1. Identifica el error exacto revisando la pestaña "Eventos" del stack. 
2. Elimina el stack fallido: selecciona el stack y haz clic en "Eliminar". 
3. Asegúrate de que todos los recursos creados se eliminen correctamente. 
4. Corrige el problema en tu template YAML. 
5. Crea un nuevo stack con el template corregido.

## Tras completar el despliegue

Una vez que tu infraestructura esté desplegada y funcionando:

1. Realiza pruebas creando, modificando y eliminando reservas. 
2. Intenta crear un conflicto (dos reservas para la misma habitación en fechas superpuestas). 
3. Verifica tu correo para confirmar que recibiste las notificaciones de conflictos. 
4. ¡Explora y disfruta de tu aplicación desplegada con CloudFormation!


# Tareas opcionales adicionales (Puntos extras)

El sistema del Hotel Cloud Suites maneja información sensible de los huéspedes, como datos personales y documentos de identidad. Es crucial proteger estos datos implementando encriptación en reposo.

### 1. Configurar encriptación en el bucket S3:

- Habilita la encriptación del lado del servidor (SSE) para el bucket de almacenamiento
- Utiliza claves administradas por AWS (SSE-S3) o mejor aún, claves administradas por KMS (SSE-KMS)
- Asegura que todos los objetos nuevos sean automáticamente cifrados

### 2. Implementar encriptación en la tabla DynamoDB:

- Configura la encriptación en reposo para la tabla de reservaciones
- Utiliza la configuración con claves administradas por AWS o KMS

### 3. Documentar la implementación:

- Explica qué tipo de encriptación elegiste y por qué
- Identifica qué datos sensibles estás protegiendo con estas medidas
- Describe cómo verificar que la encriptación está funcionando correctamente

Documentación: [Protección de datos en AWS](https://docs.aws.amazon.com/es_es/wellarchitected/latest/security-pillar/data-protection.html)

# Sistema de puntuación


La evaluación del Reto 2 se realizará de acuerdo con el siguiente sistema de puntuación:


## Creación del Template CloudFormation (70 puntos) 
Cada uno de los siguientes recursos vale 5 puntos cuando está correctamente definido: 
- AWS::S3::Bucket (S3 Bucket) 
- AWS::S3::BucketPolicy (Política del bucket) 
- AWS::DynamoDB::Table (Tabla DynamoDB) 
- AWS::SNS::Topic (Tema SNS) 
- AWS::SNS::Subscription (Suscripción SNS) 
- AWS::IAM::Role (Rol IAM para Lambda) 
- AWS::EC2::SecurityGroup (Grupo de seguridad para Lambda) 
- AWS::Lambda::Function (Función Lambda) 
- AWS::Events::Rule (Regla EventBridge) 
- AWS::Lambda::Permission (Permiso Lambda) 
- AWS::IAM::Role (Rol IAM para EC2) 
- AWS::IAM::InstanceProfile (Perfil de instancia) 
- AWS::EC2::SecurityGroup (Grupo de seguridad para EC2) 
- AWS::EC2::Instance (Instancia EC2 con UserData)

## Funcionamiento de la aplicación (20 puntos)

- Despliegue exitoso (Stack creado correctamente sin errores) - 5 puntos
- Aplicación web accesible - 5 puntos
- Aplicación funcional (crear y visualizar reservas) - 5 puntos
- Detección de conflictos (notificación por correo) - 5 puntos

## Tareas opcionales - Seguridad (10 puntos)
- Implementación de encriptación en S3 - 5 puntos
- Implementación de encriptación en DynamoDB - 5 puntos

## Registro de avance en Planner
Para registrar tu avance, deberás subir:

1. Archivo YAML completo - Sube tu template CloudFormation finalizado 
Tarea: "Template CloudFormation desarrollado" 
Adjunta: 
- Archivo .yaml completo
- Pantallazo de la validación exitosa del template en la consola de CloudFormation

2. Evidencia de despliegue - Confirma que la creación del stack fue exitosa 
Tarea: "Despliegue CloudFormation exitoso" 
Adjunta: 
- Captura de pantalla del stack con estado CREATE_COMPLETE
- Captura de pantalla de la sección Outputs del stack


3. Evidencia de funcionamiento - Demuestra que la aplicación está operativa 
Tarea: "Sistema funcionando correctamente" 
Adjunta: 
- Captura de pantalla de la página principal de la aplicación web funcionando
- Captura de pantalla de una reserva creada exitosamente
- Captura de pantalla del correo electrónico de notificación de conflicto recibido


4. Seguridad adicional (opcional) 
Tarea: "Implementación de encriptación en reposo" 
Adjunta: 
- Sección del template donde se configura la encriptación
- Breve explicación de la implementación (máximo 1 página)


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
