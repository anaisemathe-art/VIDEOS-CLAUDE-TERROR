---
name: divulgacion-3d
description: Crea guiones, shot lists, subtítulos y prompts para vídeos verticales de divulgación con animación 3D simple (estilo low-poly, cortes anatómicos/en sección, subtítulos palabra por palabra). Úsala cuando el usuario pida ideas, guiones, storyboards o prompts de vídeo explicativo para TikTok/Reels/Shorts en este estilo.
---

# divulgacion-3d

Guía de estilo basada en 3 vídeos de referencia de TikTok (divulgación de salud: dolor menstrual, posturas al dormir, mareo al levantarse; 90-120 s, 9:16). Las ideas y temas los pone el usuario; esta skill aplica el formato.

## Formato
- Vertical 9:16, 90-120 s (los 3 referentes duran 90, 94 y 118 s), ritmo rápido (cambio de plano cada 2-4 s).
- Narración continua en español, tono cercano y divulgativo, segunda persona.
- Una sola idea central; cada plano explica una pieza.

## Estructura
1. **Gancho (0-5 s):** frase intrigante o dato chocante, con el personaje en reposo. Sin saludo ni presentación.
2. **Problema:** qué le pasa al espectador o qué cree mal.
3. **Explicación visual (cuerpo del vídeo):** zoom al "interior"/mecanismo, se señalan las piezas una a una con rótulo.
4. **Giro o dato clave:** la causa menos conocida, o una cifra (ej. "5 años").
5. **Cierre:** llamada a comentar (burbuja de chat + flecha + mascota).

## Estilo visual
- Personaje 3D simple de perfil, formas redondeadas, sin rasgos detallados (ej. jersey rosa, pantalón lila).
- Fondo blanco/gris muy claro con suelo y sombra suave.
- Paleta pastel: rosa, rojo suave, amarillo, lila, azul claro.
- Cortes en sección y zooms al interior, con elementos resaltados en amarillo/rojo.
- Iconos de apoyo: "?", rayo, calendario, fila de personitas, burbuja de chat, mascota con casco amarillo.
- Cámara siempre en movimiento suave (zoom, paneo).

## Texto en pantalla
- Subtítulos palabra por palabra, MAYÚSCULAS, parte inferior, fuente tipo pixel.
- Rótulo grande de color (amarillo/rojo) para el término clave, sobre el elemento que se señala.
- Marca de agua/usuario en la esquina.

## Prompt base de imagen/vídeo
`simple 3D low-poly animated explainer, pastel colors, white clean background, rounded stylized character in profile, cross-section anatomy view, soft shadows, vertical 9:16, yellow highlight labels`

## Entrega
```
TÍTULO:
GANCHO (frase exacta):
DURACIÓN:

| T | Plano | Narración | Rótulo/Icono | Movimiento de cámara |
|---|-------|-----------|--------------|----------------------|

PROMPTS VISUALES (uno por plano):
CIERRE / CTA:
```

## Patrones confirmados en los 3 vídeos
- **Tema = pregunta cotidiana de salud** ("¿cuál es la postura correcta?", "¿por qué me mareo al levantarme?") respondida mostrando el interior del cuerpo.
- **Mismo mundo 3D en todos:** dormitorio/casa low-poly con colores azul-lila-crema, personaje sin rasgos detallados (cambia de ropa/género según el vídeo), cuerpo con transparencia para ver órganos.
- **Órganos con personalidad:** el cerebro con ojos cartoon; flechas, medidores y barras de nivel (presión, sangre, oxígeno), cronómetros y termómetros para mostrar cambios.
- **Estructura por lista o pasos:** casos comparados (boca abajo / boca arriba / lado derecho / lado izquierdo) o "PASO 1, PASO 2"; cada uno con rótulo amarillo y veredicto.
- **Veredicto visual:** ✕ rojo = mal, ✓ verde = bien; rótulos rojos para lo negativo ("LA PEOR", "MENOS SANGRE"), amarillos para términos clave.
- **Analogías cotidianas:** ej. manguera para el flujo de sangre, estrellitas para el mareo.
- **Término técnico** aparece una vez en rótulo (ej. "HIPOTENSIÓN ORTOSTÁTICA") tras explicarlo en simple.
- **Solución práctica** al final del cuerpo (qué hacer) antes del cierre.
- **Cierre fijo:** mascota con casco amarillo + burbuja de chat "..." (llamada a comentar) y pantalla final de TikTok con el usuario.
- Transiciones por zoom/desenfoque entre plano exterior e interior; cámara cenital o lateral según la escena.

## Voz en off
- API: `https://api.vibi.pro` (cabecera `xi-api-key`; la clave NO va en el repo, la inyecta el proxy del entorno).
- Texto a voz: `POST /v1/text-to-speech/{voice_id}` con `{"text","provider","language_code","model_id"?,"voice_settings"?}` → devuelve `{id,status:"pending"}`.
- Resultado: consultar `GET /v1/history/{id}` hasta `status=completed`; el MP3 está en `result.audio_url`. Saldo: `GET /v1/auth/me`.
- Voz del usuario: `ojGau167OE7nUATM1xDa` con `provider=elevenlabs`, `model_id=eleven_v3`, `language_code=es`, `voice_settings.stability=0.5` (probada OK el 2026-11-21: ~3 s de audio, 43 créditos por 45 caracteres aprox.). El ID antiguo `7477926365174436369` no funcionó (MiniMax: no encontrada; CapCut: mantenimiento; ElevenLabs: se quedó colgada).
- Redactar la narración para locución: frases cortas, sin siglas ni símbolos, números en palabras.

## Escenarios (preferencia del usuario, 2026-11-21)
- Nada de fondos blancos o planos: se ven poco profesionales.
- El lugar cambia según el tema del vídeo (cocina para comida, dormitorio para sueño, baño, oficina, gimnasio…).
- Siempre con detalle y profundidad: muebles, objetos, ventana, plantas; iluminación cálida, sombras suaves, desenfoque de fondo (profundidad de campo) en primeros planos.
- Personaje principal: el avatar 3D del usuario (pendiente de recibir el archivo .glb/.fbx/.obj).
