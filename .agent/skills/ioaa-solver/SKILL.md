---
name: ioaa-solver
description: Guia de resolução física, mecânica celeste e modelagem astronômica para problemas da IOAA / Olimpíadas de Astronomia
---

# IOAA Problem Solver Skill

Esta skill instrui o agente a ler, analisar e extrair as equações físicas e parâmetros para simulações astronômicas a partir de enunciados de olimpíadas.

## Fluxo de Extração de Problemas
1. **Identificar o Sistema Físico**:
   - Corpos centrais (Massa $M$, Raio $R$, Temperatura $T$, Luminosidade $L$).
   - Corpos orbitantes / secundários (semi-eixo maior $a$, excentricidade $e$, inclinação $i$, longitude do nó ascendente $\Omega$, argumento do periastro $\omega$).
   - Ponto de vista do observador (Geocêntrico, Topocêntrico com latitude $\phi$, ou Ponto Lagrangeano).

2. **Cálculos Numéricos / Analíticos**:
   - Usar `astropy` e `scipy` para integração orbital (Kepler analítico ou integrador N-corpos Runge-Kutta).
   - Conversão de coordenadas esféricas (Ascensão Reta $\alpha$, Declinação $\delta$) para coordenadas cartesianas $(X, Y, Z)$ no referencial da cena.

3. **Geração de Dados Estruturados**:
   - Gerar um arquivo `params.json` contendo:
     - Escala de distâncias (1 unidade Blender = $X$ UA ou $X$ km).
     - Escala de tempo (1 segundo de vídeo = $T$ dias/anos).
     - Posições dos corpos em função do tempo $t$.
