# Configuración del dominio propio

El sitio puede publicarse primero en GitHub Pages y conectar un dominio después. No es necesario modificar los componentes ni las rutas. La compra del dominio no está incluida: exige una decisión, datos del titular y un pago del propietario.

## 1. Recomendación y verificación actual

La primera opción recomendada es `laberintofiscal.co`: coincide con el nombre del libro, conserva una dirección corta y refuerza su relación con Colombia. Como protección opcional, puede registrarse también `laberintofiscal.com` y redirigirlo al dominio principal. `laberintofiscal.com.co` es reconocible en Colombia, pero es más largo; `laberintofiscal.org` puede sugerir que el sitio pertenece a una organización independiente.

Consulta realizada el 19 de agosto de 2026:

| Dominio | Resultado de la consulta registral |
|---|---|
| `laberintofiscal.co` | Sin registro RDAP encontrado |
| `laberintofiscal.com.co` | Sin registro RDAP encontrado |
| `laberintofiscal.org` | Sin registro RDAP encontrado |
| `laberintofiscal.com` | Sin registro RDAP encontrado |

Un resultado RDAP «no encontrado» indica que no existe un registro visible en ese momento, pero no reserva el nombre ni sustituye la comprobación del registrador. La disponibilidad definitiva y el carácter estándar o *premium* deben confirmarse en el carrito inmediatamente antes del pago.

Precios observados el mismo día para dominios estándar de un año:

| Extensión y registrador | Registro | Renovación |
|---|---:|---:|
| `.co` en [Porkbun](https://porkbun.com/products/domains) | USD 15,76 en promoción | USD 31,20 |
| `.co` en [MI.COM.CO](https://mi.com.co/dominios) | COP 19.990 en promoción | COP 229.990 |
| `.com.co` en [MI.COM.CO](https://mi.com.co/dominios) | COP 14.990 en promoción | COP 149.990 |
| `.org` en [Porkbun](https://porkbun.com/products/domains) | USD 7,98 en promoción | USD 11,84 |
| `.org` en [MI.COM.CO](https://mi.com.co/dominios) | COP 94.990 | COP 94.990 |
| `.com` en [Porkbun](https://porkbun.com/products/domains) | USD 11,08 | USD 11,08 |

Los precios, impuestos y promociones pueden cambiar. Porkbun ofrece un costo de renovación menor en la comparación consultada; MI.COM.CO cobra en pesos, ofrece factura colombiana y puede resultar más sencillo para pagos locales. Cloudflare Registrar también admite `.co` y `.org` con precios sin margen sobre la tarifa del registro, pero el valor exacto debe verificarse dentro de su buscador antes de decidir.

Además del precio, conviene comparar la privacidad de los datos del titular, el soporte de DNS, los costos de transferencia, la moneda de cobro y la facilidad para descargar el código de autorización. No se ha comprado ni reservado ningún dominio.

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
