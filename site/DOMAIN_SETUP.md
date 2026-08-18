# Configuración del dominio propio

El sitio puede publicarse primero en GitHub Pages y conectar un dominio después. No es necesario modificar los componentes ni las rutas. La compra del dominio no está incluida: exige una decisión, datos del titular y un pago del propietario.

## 1. Buscar y comparar

Consultar en un registrador acreditado la disponibilidad, el precio del primer año y —sobre todo— el precio de renovación de:

- `laberintofiscal.co`
- `laberintofiscal.com.co`
- `laberintofiscal.org`

`laberintofiscal.co` aparecía dos veces en la lista inicial; aquí se presenta una sola vez. No se afirma que ninguno esté disponible. La verificación debe hacerse inmediatamente antes de la compra, pues tanto la disponibilidad como el precio cambian.

Comparar también: privacidad de los datos del titular, soporte de DNS, costos de transferencia, moneda de cobro y facilidad para descargar el código de autorización.

## 2. Registrar con control institucional claro

Registrar el dominio a nombre de Oliver Pardo o de la entidad que deba conservar su control. El correo de recuperación no debe depender de un proveedor temporal. Después de comprar:

1. activar la renovación automática;
2. activar autenticación de dos factores;
3. guardar los códigos de recuperación;
4. activar el bloqueo de transferencia;
5. registrar internamente la fecha y el costo de renovación.

## 3. Verificar el dominio en GitHub

En la cuenta propietaria del repositorio, abrir `Settings → Pages → Verified domains` y solicitar la verificación. GitHub mostrará un registro TXT específico, con un nombre parecido a:

```text
_github-pages-challenge-oliverpardo1979.DOMINIO-ELEGIDO
```

Crear exactamente el TXT que GitHub indique, esperar a que se propague y completar la verificación. No eliminar después ese TXT. La verificación reduce el riesgo de que otra cuenta intente apropiarse del dominio o de un subdominio. Véase la [documentación oficial de verificación de GitHub Pages](https://docs.github.com/en/pages/configuring-a-custom-domain-for-your-github-pages-site/verifying-your-custom-domain-for-github-pages).

## 4. Declarar el dominio en el repositorio

En `Settings → Pages → Custom domain`, usar como URL canónica:

```text
www.DOMINIO-ELEGIDO
```

GitHub recomienda configurar tanto el dominio raíz como `www`; puede redirigir uno hacia el otro cuando ambos registros son correctos. Es más seguro declarar el dominio en GitHub antes de crear los registros DNS públicos. Consulte [Administrar un dominio personalizado para GitHub Pages](https://docs.github.com/es/pages/configuring-a-custom-domain-for-your-github-pages-site/managing-a-custom-domain-for-your-github-pages-site).

## 5. Configurar el DNS

Para el dominio raíz `@`, crear cuatro registros A:

| Tipo | Nombre | Destino |
|---|---|---|
| A | `@` | `185.199.108.153` |
| A | `@` | `185.199.109.153` |
| A | `@` | `185.199.110.153` |
| A | `@` | `185.199.111.153` |

Para `www`:

| Tipo | Nombre | Destino |
|---|---|---|
| CNAME | `www` | `oliverpardo1979.github.io` |

El CNAME no debe incluir `/20250626_LaberintoFiscalObs` ni ninguna ruta. No crear registros comodín como `*.DOMINIO-ELEGIDO`: GitHub advierte que aumentan el riesgo de toma de subdominios.

## 6. Ajustar las variables del build

En `Settings → Secrets and variables → Actions → Variables`, crear o actualizar:

```text
SITE_URL=https://www.DOMINIO-ELEGIDO
BASE_PATH=/
```

Volver a ejecutar el workflow **Build and deploy book site**. Esto actualiza las URL canónicas, Open Graph, `sitemap.xml` y todos los enlaces internos.

## 7. Verificar desde Windows

En PowerShell:

```powershell
Resolve-DnsName DOMINIO-ELEGIDO
Resolve-DnsName www.DOMINIO-ELEGIDO
```

El primer comando debe mostrar las cuatro direcciones A. El segundo debe resolver el CNAME hacia `oliverpardo1979.github.io`. Los cambios de DNS pueden tardar hasta 24 horas en propagarse.

## 8. Activar HTTPS

Cuando GitHub haya emitido el certificado, regresar a `Settings → Pages` y activar **Enforce HTTPS**. Probar:

- `https://DOMINIO-ELEGIDO`
- `https://www.DOMINIO-ELEGIDO`
- una URL profunda de capítulo;
- la redirección de HTTP a HTTPS.

GitHub Pages admite HTTPS en dominios correctamente configurados; la [guía oficial de HTTPS](https://docs.github.com/es/pages/getting-started-with-github-pages/securing-your-github-pages-site-with-https) explica también qué registros adicionales pueden impedir la emisión del certificado.

