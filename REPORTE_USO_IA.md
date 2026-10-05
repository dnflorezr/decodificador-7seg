# Reporte de uso de IA y trabajo colaborativo

**Taller de segundo corte · Sistemas Digitales 2026-2**
**Estudiante:** Diego Florez · **Asistente de IA:** Claude (Anthropic), usado en Claude Code
**Repositorio:** <https://github.com/dnflorezr/decodificador-7seg>

Este taller se hizo como una colaboración entre el estudiante y un asistente de IA. Este documento
declara cómo se repartió el trabajo, qué prompts se usaron y qué se verificó en el equipo del estudiante.

## 1. Declaración

La guía del taller indica que un asistente de IA no debe redactar la solución completa. Al recibir el
enunciado, el asistente lo señaló y preguntó cómo proceder. El estudiante decidió que la IA generara en conjunto con el estudiante
los entregables y que, al final, le explicara el funcionamiento en detalle. Esa decisión y su
responsabilidad son del estudiante. La guía también advierte que el código Python generado por una IA
podría traer errores; por eso todo se ejecutó y se verificó (sección 4).

## 2. Reparto de roles

| Parte | Asistente de IA | Estudiante |
|---|---|---|
| Lectura de la guía y del script base | Descargó y revisó `sevensegdec.py` antes de ejecutarlo | Aportó la guía y decidió el alcance |
| Tabla de decodificación y símbolos 10–15 | Propuso la tabla y las justificaciones | Revisión y aprobación de las decisiones (1 a la derecha, 6/9 cerrados) |
| Simulación y HDL | Ejecutó el script, generó VCD, VHDL y Verilog | Repitió la simulación en su equipo |
| Pruebas con pytest | Escribió la versión modificada y las pruebas; inyectó errores para comprobar que se detectan | Ejecución local |
| README y figuras | Redactó el informe y los scripts de figuras | Revisión del contenido |
| Entorno local | Guió la instalación paso a paso | Instaló, depuró los errores y ejecutó los comandos |
| GitHub | Indicó los comandos | Creó el repositorio, corrigió el usuario y publicó (`git push`) |

## 3. Prompts usados

| # | Prompt (resumen) | Qué produjo la IA |
|:-:|---|---|
| 1 | Enunciado completo del taller: tabla de 16 entradas, uso de `sevensegdec.py`, resultados de simulación y VCD, pruebas unitarias y repositorio listo para GitHub | Lectura de la guía en PDF y del script base. Aviso de que la guía limita la ayuda de la IA |
| 2 | "Hazlo completo, pero al final dame a mí la retroalimentación detallada del funcionamiento" | `tabla.txt`, HDL (VHDL y Verilog), VCD, `sevensegdec_mod.py`, `test_sevensegdec.py`, README con figuras y ecuaciones. Explicación final del funcionamiento |
| 3 | Guíame paso a paso para simular y correr el programa de forma local; tengo que instalar los programas | Guía de 9 pasos: entorno virtual, dependencias, simulación, pytest, GTKWave y GitHub |
| 4 | Capturas del error `No module named pip` | Diagnóstico: `python` apuntaba al Python de MSYS2; solución con entorno virtual |
| 5 | Captura del bloqueo de `Activate.ps1` | Cambio de la política de ejecución de PowerShell para el usuario actual |
| 6 | Captura de `FileNotFoundError` al crear el VCD | Prueba de escritura que aisló la causa (carpeta de OneDrive) y solución: trabajar en `C:\Users\diego\7seg` |
| 7 | Capturas de los errores de `git push` (marcador `<tu-usuario>`, puerto 443, repositorio no encontrado) | Corrección con `git remote set-url`, comprobación de red y de que el repositorio existiera |
| 8 | Captura de GitHub con el repositorio vacío | Identificó el usuario correcto (`dnflorezr`) |
| 9 | "Justifica por qué se usaron 66 pruebas, eran necesarias todas y si es mejor hacer solo las necesarias" | Análisis de redundancia (sección 5) |
| 10 | Solicitud de este reporte (colaboración estudiante–IA) | Este documento |

## 4. Qué se verificó y cómo

- **Script base:** se leyó el código completo antes de ejecutarlo y se comprobó que no hacía nada ajeno al enunciado.
- **Simulación y HDL:** el asistente generó VHDL y Verilog con la tabla y verificó que ambos VCD fueran idénticos. El estudiante repitió la simulación VHDL en su equipo y obtuvo `Simulation done. / Conversion done (VHDL).`
- **Pruebas:** 66 pruebas pasaron en el entorno del asistente.
- **Detección de errores:** se introdujeron tres errores a propósito (6 abierto, decodificador sin inversión, LUT mal indexada) y las pruebas los detectaron: fallaron 4, 16 y 32 pruebas respectivamente.
- **Ecuaciones booleanas:** se comprobaron las 7 sumas de productos contra la tabla de verdad con un chequeo independiente.
- **Figuras:** se revisaron visualmente en el navegador. No son capturas de GTKWave; se generan con `herramientas/generar_figuras.py` a partir del VCD real.
- **Publicación:** se comprobó que el repositorio público contiene todas las carpetas y archivos esperados.

## 5. Revisión crítica de las 66 pruebas

Las 66 pruebas salen de 16 valores × 3 pruebas parametrizadas (48) más 18 pruebas sueltas. No todas eran necesarias:

- `test_table_file_matches_spec` (16) es casi redundante con `test_decoder_output` (16): ante un error en la tabla fallan las dos a la vez.
- `test_decoder_inverted_output` (16) verifica una sola línea del código; una prueba que recorra las 16 entradas bastaría.
- `test_symbols_10_15_are_not_hex_letters` (7) verifica una sola regla.

Una suite de unas 30 pruebas detectaría los mismos errores. Se conservan la parametrización de los 16 casos (la pide la guía), las pruebas de `read_table` y las de conversión a HDL, porque cada una detecta un fallo distinto. Este recorte **no se ha aplicado**; queda como decisión del estudiante.

## 6. Limitaciones y aprendizajes

- El testbench original verifica consistencia, no corrección: compara el resultado contra la misma tabla con la que se construyó el decodificador. Las pruebas nuevas usan una especificación independiente.
- El script original falla en silencio con tablas mal formadas (línea en blanco o 15 líneas). La versión modificada lo convierte en un error explícito.
- Las opciones del script llevan doble guion (`--table`), a diferencia del ejemplo del enunciado.
- Problemas de entorno resueltos: Python de MSYS2 sin pip, política de ejecución de PowerShell, escritura en carpetas de OneDrive y usuario de GitHub equivocado.

## 7. Lo que el estudiante debe poder explicar

Si se pregunta por el trabajo, el estudiante debe poder responder con sus palabras:
1. Qué representa cada bit de `sseg` y por qué `a` es el bit 6.
2. Por qué el testbench original no muestra ERROR con una tabla consistente.
3. Cómo `decod_table[int(bcd)]` se convierte en un `case` y por qué es lógica combinacional.
4. Qué hace `@pytest.mark.parametrize` y por qué `SPEC` es independiente de `tabla.txt`.
5. Por qué se eligió el 6 y el 9 cerrados, y el 1 a la derecha.
