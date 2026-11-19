#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PRACTICADOR DE INTEGRALES - Análisis Matemático 6to año - Guía 1
-----------------------------------------------------------------
Cómo usarlo:
    1) Instalá Python 3 (python.org) si no lo tenés.
    2) Abrí una terminal en la carpeta donde guardaste este archivo.
    3) Escribí:   python integrales.py      (en Mac/Linux: python3 integrales.py)

No necesita instalar nada más.

Cómo corrige:
    Tu respuesta es correcta si al DERIVARLA da la función que estaba
    dentro de la integral (la constante C no importa porque al derivar desaparece).
    Eso significa que cualquier forma equivalente de escribir la respuesta cuenta como bien.
"""

import math
import re
import sys
import textwrap

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

# ----------------------------------------------------------------------
# 1) LEER LO QUE ESCRIBE EL USUARIO Y CONVERTIRLO EN UNA FUNCIÓN
# ----------------------------------------------------------------------


def _ln(x):
    # ln|x|: usamos valor absoluto para que no importe el signo
    return math.log(abs(x))


NOMBRES = {
    "sin": math.sin, "sen": math.sin,
    "cos": math.cos,
    "tan": math.tan, "tg": math.tan,
    "cotg": lambda x: 1 / math.tan(x), "cot": lambda x: 1 / math.tan(x),
    "sec": lambda x: 1 / math.cos(x),
    "cosec": lambda x: 1 / math.sin(x),
    "exp": math.exp,
    "ln": _ln, "log": _ln,
    "sqrt": math.sqrt, "raiz": math.sqrt,
    "arcsen": math.asin, "arcsin": math.asin, "asin": math.asin,
    "arctg": math.atan, "arctan": math.atan, "atan": math.atan,
    "abs": abs,
    "pi": math.pi, "e": math.e,
}


def preparar(texto):
    """Arregla la forma de escribir para que Python la entienda."""
    t = texto.strip().lower()
    t = t.lstrip("=").strip()
    t = t.replace("−", "-").replace("–", "-").replace("·", "*").replace("×", "*")
    t = t.replace("π", "pi").replace("√", "raiz").replace(",", ".")
    t = t.replace("^", "**")
    t = t.replace("²", "**2").replace("³", "**3")
    # ln|x+3|  ->  ln(x+3)
    t = re.sub(r"ln\|([^|]*)\|", r"ln(\1)", t)
    # sacar el "+ C" del final
    t = re.sub(r"\s*\+\s*c\s*$", "", t)
    # funciones sin paréntesis: "cos x" -> "cos(x)"
    t = re.sub(r"\b(sin|sen|cos|tan|tg|cotg|cot|sec|cosec|ln|log|exp|sqrt|raiz|arcsen|arctg)\s*x\b", r"\1(x)", t)
    # multiplicación implícita: 3x -> 3*x ; )( -> )*( ; x( -> x*(
    t = re.sub(r"(\d)\s*(?=[a-z(])", r"\1*", t)
    t = re.sub(r"\)\s*(?=[a-z0-9(])", ")*", t)
    t = re.sub(r"\b(x|e|pi)\s*(?=\()", r"\1*", t)
    t = re.sub(r"\b(x|e|pi)\s+(?=[a-z0-9(])", r"\1*", t)
    return t


class ErrorDeFormato(Exception):
    pass


def crear_funcion(texto):
    codigo = preparar(texto)
    try:
        compilado = compile(codigo, "<respuesta>", "eval")
    except SyntaxError:
        raise ErrorDeFormato("No pude entender cómo escribiste la respuesta (revisá los paréntesis y los signos).")

    def F(x):
        return eval(compilado, {"__builtins__": {}}, dict(NOMBRES, x=x))

    return F


# ----------------------------------------------------------------------
# 2) CORREGIR: derivar la respuesta del usuario y compararla
# ----------------------------------------------------------------------


def derivada(F, x, h=1e-5):
    return (F(x + h) - F(x - h)) / (2 * h)


def comparar(F, ej):
    """Devuelve una lista de (x, derivada_de_tu_respuesta, integrando)."""
    pares = []
    for x in ej["puntos"]:
        try:
            d = derivada(F, x)
            v = ej["f"](x)
        except (ValueError, ZeroDivisionError, OverflowError):
            continue
        except NameError as err:
            raise ErrorDeFormato("No conozco '%s'. Usá x, sen(x), cos(x), tg(x), ln(x), e^x, pi, etc." % err.name)
        except TypeError:
            raise ErrorDeFormato("Hay algo mal escrito. Si multiplicás letras usá *, por ejemplo x*sen(x).")
        if isinstance(d, complex) or isinstance(v, complex):
            continue
        if math.isnan(d) or math.isinf(d):
            continue
        pares.append((x, d, v))
    if len(pares) < 3:
        raise ErrorDeFormato("No pude evaluar tu respuesta. Revisá cómo la escribiste (tipeá 'ayuda').")
    return pares


def es_correcta(pares):
    return all(abs(d - v) <= 1e-4 * (1 + abs(v)) for _, d, v in pares)


def diagnostico(pares):
    """Intenta explicar QUÉ salió mal mirando cómo se parece tu derivada al integrando."""
    msgs = []
    # ¿La derivada es k veces el integrando?
    razones = [d / v for _, d, v in pares if abs(v) > 1e-6]
    if len(razones) >= 3 and max(razones) - min(razones) <= 1e-3 * (1 + abs(razones[0])):
        k = sum(razones) / len(razones)
        if abs(k + 1) < 1e-3:
            msgs.append("Te quedó el SIGNO al revés (al derivar tu respuesta sale el integrando pero con signo cambiado).")
        elif k > 1:
            msgs.append("Al derivar tu respuesta sale %.4g veces el integrando: te SOBRA ese factor. "
                        "Si usaste sustitución, ¿te olvidaste de dividir por la derivada de lo de adentro (du)?" % k)
        else:
            msgs.append("Al derivar tu respuesta sale %.4g veces el integrando: te FALTA multiplicar por %.4g. "
                        "Si usaste sustitución, fijate si dividiste de más al pasar de dx a du." % (k, 1 / k))
        return msgs
    # ¿Se diferencia en una constante?
    difs = [d - v for _, d, v in pares]
    if max(difs) - min(difs) <= 1e-3:
        c = sum(difs) / len(difs)
        msgs.append("Tu derivada se pasa/le falta un número fijo (%.4g). Revisá los términos que son solo un número: "
                    "la integral de un número k es k·x, no k." % c)
        return msgs
    msgs.append("Al derivar tu respuesta NO da el integrando. Comparación en algunos puntos:")
    for x, d, v in pares[:3]:
        msgs.append("   en x = %-6g  tu derivada = %-12.6g  el integrando = %.6g" % (x, d, v))
    msgs.append("Tip: derivá tu respuesta paso a paso y fijate en qué término se aleja.")
    return msgs


# ----------------------------------------------------------------------
# 3) LOS EJERCICIOS DE LA GUÍA
# ----------------------------------------------------------------------

EJERCICIOS = []


def ej(id_, enunciado, metodo, f, puntos, resp, resp_in, pista, pasos):
    EJERCICIOS.append(dict(id=id_, enunciado=enunciado, metodo=metodo, f=f, puntos=puntos,
                           resp=resp, resp_in=resp_in, pista=pista,
                           pasos=textwrap.dedent(pasos).strip("\n")))


P_BASE = [-1, 0, 0.5, 1, 2]
sin, cos, tan, exp, log, sqrt, pi, e = math.sin, math.cos, math.tan, math.exp, math.log, math.sqrt, math.pi, math.e

M1 = "Integral inmediata (de tabla)"
M2 = "Sustitución"
M3 = "Integración por partes"
M4 = "Fracciones simples"

# ---------------- 1) Integrales indefinidas ----------------
ej("1a", "∫ (−eˣ + e) dx", M1, lambda x: -exp(x) + e, P_BASE,
   "−eˣ + e·x + C", "-e^x + e*x",
   "e es un número (2,718...), así que se integra como una constante: e·x.",
   """
   Integro cada parte. −eˣ pasa a −eˣ, y e es un número, así que pasa a e·x.
   = −eˣ + e·x + C
   """)
ej("1b", "∫ (3x² − 3x + eˣ) dx", M1, lambda x: 3 * x**2 - 3 * x + exp(x), P_BASE,
   "x³ − (3/2)x² + eˣ + C", "x^3 - (3/2)x^2 + e^x",
   "Para xⁿ: subí el exponente en 1 y dividí por el exponente nuevo.",
   """
   - 3x²  → 3·x³/3 = x³
   - −3x  → −3·x²/2
   - eˣ   → eˣ
   = x³ − (3/2)x² + eˣ + C
   """)
ej("1c", "∫ (sen x − π) dx", M1, lambda x: sin(x) - pi, P_BASE,
   "−cos x − π·x + C", "-cos(x) - pi*x",
   "∫sen x dx = −cos x. π es un número: se integra como constante.",
   """
   π es un número, así que se integra como constante.
   = −cos x − π·x + C
   """)
ej("1d", "∫ (1/cos²x + 1/sen²x) dx", M1, lambda x: 1 / cos(x)**2 + 1 / sin(x)**2, [0.3, 0.7, 1.0, 1.2, 2.0],
   "tg x − cotg x + C", "tg(x) - cotg(x)",
   "Son dos integrales de tabla: ∫1/cos²x dx = tg x y ∫1/sen²x dx = −cotg x.",
   """
   Son integrales de tabla:
   ∫1/cos²x dx = tg x
   ∫1/sen²x dx = −cotg x
   = tg x − cotg x + C
   """)
ej("1e", "∫ 2/√(1−x²) dx", M1, lambda x: 2 / sqrt(1 - x**2), [-0.6, -0.2, 0.1, 0.4, 0.8],
   "2·arcsen x + C", "2*arcsen(x)",
   "El 2 sale multiplicando. ∫1/√(1−x²) dx = arcsen x (tabla).",
   """
   El 2 sale multiplicando. ∫1/√(1−x²) dx = arcsen x (tabla).
   = 2·arcsen x + C
   """)
ej("1f", "∫ 5/(1+x²) dx", M1, lambda x: 5 / (1 + x**2), P_BASE,
   "5·arctg x + C", "5*arctg(x)",
   "El 5 sale multiplicando. ∫1/(1+x²) dx = arctg x (tabla).",
   """
   El 5 sale multiplicando. ∫1/(1+x²) dx = arctg x (tabla).
   = 5·arctg x + C
   """)
ej("1g", "∫ (2·tg x − 3) dx", M1, lambda x: 2 * tan(x) - 3, [0.2, 0.5, 0.8, 1.1, -0.4],
   "−2·ln|cos x| − 3x + C", "-2*ln(cos(x)) - 3*x",
   "Se separa en 2∫tg x dx − ∫3 dx. De tabla, ∫tg x dx = −ln|cos x|.",
   """
   Se separa en 2∫tg x dx − ∫3 dx.
   De tabla, ∫tg x dx = −ln|cos x|.
   = −2·ln|cos x| − 3x + C
   """)

# ---------------- 2) Sustitución ----------------
ej("2a", "∫ (x − 1)⁵ dx", M2, lambda x: (x - 1)**5, P_BASE,
   "(x−1)⁶/6 + C", "(x-1)^6/6",
   "Probá u = x − 1. ¿Cuánto vale du?",
   """
   u = x − 1, entonces du = dx
   ∫u⁵ du = u⁶/6
   = (x−1)⁶/6 + C
   """)
ej("2b", "∫ (6/5)·x·cos(x² − π) dx", M2, lambda x: 6 / 5 * x * cos(x**2 - pi), P_BASE,
   "(3/5)·sen(x² − π) + C", "(3/5)*sen(x^2 - pi)",
   "u = x² − π. Fijate que du = 2x dx, y arriba tenés x dx.",
   """
   u = x² − π, entonces du = 2x dx, o sea x dx = du/2
   (6/5)·(1/2)∫cos u du = (3/5)·sen u
   = (3/5)·sen(x² − π) + C
   """)
ej("2c", "∫ (3x − 2)^(1/3) dx", M2, lambda x: (3 * x - 2)**(1 / 3), [1, 1.5, 2, 3, 4],
   "(1/4)(3x−2)^(4/3) + C", "(1/4)*(3x-2)^(4/3)",
   "u = 3x − 2, du = 3dx, entonces dx = du/3. Después es una potencia.",
   """
   u = 3x − 2, entonces du = 3dx, o sea dx = du/3
   (1/3)∫u^(1/3) du = (1/3)·u^(4/3)/(4/3) = (1/3)·(3/4)·u^(4/3) = (1/4)·u^(4/3)
   = (1/4)(3x−2)^(4/3) + C
   """)
ej("2d", "∫ 3x²/(x³ + 3) dx", M2, lambda x: 3 * x**2 / (x**3 + 3), [-1, 0, 0.5, 1, 2],
   "ln|x³ + 3| + C", "ln(x^3 + 3)",
   "u = x³ + 3. ¿Cuánto da du? Fijate que arriba ya está.",
   """
   u = x³ + 3, entonces du = 3x² dx (justo lo que está arriba)
   ∫1/u du = ln|u|
   = ln|x³ + 3| + C
   """)
ej("2e", "∫ sen x · cos x dx", M2, lambda x: sin(x) * cos(x), P_BASE,
   "sen²x/2 + C", "sen(x)^2/2",
   "u = sen x, entonces du = cos x dx.",
   """
   u = sen x, entonces du = cos x dx
   ∫u du = u²/2
   = sen²x/2 + C
   """)
ej("2f", "∫ sen(5x − 2) dx", M2, lambda x: sin(5 * x - 2), P_BASE,
   "−(1/5)·cos(5x − 2) + C", "-(1/5)*cos(5x-2)",
   "u = 5x − 2, du = 5dx, entonces dx = du/5.",
   """
   u = 5x − 2, entonces du = 5dx, o sea dx = du/5
   (1/5)∫sen u du = −(1/5)cos u
   = −(1/5)cos(5x − 2) + C
   """)
ej("2g", "∫ 4x · sen(x² + 1) · cos(x² + 1) dx", M2,
   lambda x: 4 * x * sin(x**2 + 1) * cos(x**2 + 1), P_BASE,
   "sen²(x² + 1) + C", "sen(x^2 + 1)^2",
   "u = x² + 1, du = 2x dx, entonces 4x dx = 2 du. Después queda como el ejercicio 2e.",
   """
   u = x² + 1, entonces du = 2x dx, o sea 4x dx = 2du
   2∫sen u·cos u du. Esta integral es la del ejercicio e), que da sen²u/2.
   2·(sen²u/2) = sen²u
   = sen²(x² + 1) + C
   """)

# ---------------- 3) Por partes ----------------
ej("3a", "∫ (1 + 3x) · e^(3x−1) dx", M3, lambda x: (1 + 3 * x) * exp(3 * x - 1), [-1, 0, 0.5, 1],
   "x·e^(3x−1) + C", "x*e^(3x-1)",
   "u = 1+3x (al derivar se achica), dv = e^(3x−1) dx.",
   """
   u = 1+3x  → du = 3dx
   dv = e^(3x−1)dx → v = e^(3x−1)/3
   = (1+3x)·e^(3x−1)/3 − ∫e^(3x−1) dx
   = (1+3x)·e^(3x−1)/3 − e^(3x−1)/3
   Saco factor común e^(3x−1)/3: (1+3x−1) = 3x
   = x·e^(3x−1) + C
   """)
ej("3b", "∫ e^(3x) · (x + 2) dx", M3, lambda x: exp(3 * x) * (x + 2), [-1, 0, 0.5, 1],
   "e^(3x)·(3x + 5)/9 + C", "e^(3x)*(3x+5)/9",
   "u = x+2, dv = e^(3x) dx.",
   """
   u = x+2 → du = dx
   dv = e^(3x)dx → v = e^(3x)/3
   = (x+2)·e^(3x)/3 − (1/3)∫e^(3x) dx
   = (x+2)·e^(3x)/3 − e^(3x)/9
   Factor común e^(3x)/9: (3x+6−1)
   = e^(3x)·(3x+5)/9 + C
   """)
ej("3c", "∫ x · (5 + x)² dx", M3, lambda x: x * (5 + x)**2, P_BASE,
   "(5+x)³·(3x − 5)/12 + C", "(5+x)^3*(3x-5)/12",
   "u = x, dv = (5+x)² dx. (También se puede resolver desarrollando el cuadrado.)",
   """
   u = x → du = dx
   dv = (5+x)²dx → v = (5+x)³/3
   = x(5+x)³/3 − (1/3)∫(5+x)³ dx
   = x(5+x)³/3 − (5+x)⁴/12
   Factor común (5+x)³/12: (4x − (5+x)) = 3x − 5
   = (5+x)³·(3x−5)/12 + C
   """)
ej("3d", "∫ x^(−1/2) · ln x dx", M3, lambda x: x**(-0.5) * log(x), [0.5, 1, 2, 3, 4],
   "2√x·ln x − 4√x + C", "2*sqrt(x)*ln(x) - 4*sqrt(x)",
   "u = ln x (su derivada es más simple), dv = x^(−1/2) dx.",
   """
   u = ln x → du = dx/x
   dv = x^(−1/2)dx → v = 2x^(1/2) = 2√x
   = 2√x·ln x − ∫2√x·(1/x) dx
   √x/x = x^(−1/2), así que queda 2∫x^(−1/2) dx = 2·2√x = 4√x
   = 2√x·ln x − 4√x + C
   """)
ej("3e", "∫ (x³ + 7x − 2) · eˣ dx", M3, lambda x: (x**3 + 7 * x - 2) * exp(x), [-1, 0, 0.5, 1, 2],
   "eˣ·(x³ − 3x² + 13x − 15) + C", "e^x*(x^3 - 3x^2 + 13x - 15)",
   "Hay que repetir partes 3 veces: u = el polinomio, dv = eˣ dx. Cada vez el grado baja 1.",
   """
   Hay que repetir partes varias veces, porque cada vez el polinomio baja de grado.
   - 1ª vez: u = x³+7x−2, dv = eˣdx → (x³+7x−2)eˣ − ∫(3x²+7)eˣ dx
   - 2ª vez: u = 3x²+7 → (3x²+7)eˣ − ∫6x·eˣ dx
   - 3ª vez: u = 6x → 6x·eˣ − ∫6eˣ dx = 6x·eˣ − 6eˣ
   Armo todo, con los signos que van alternando:
   eˣ·[(x³+7x−2) − (3x²+7) + 6x − 6]
   = eˣ·(x³ − 3x² + 13x − 15) + C
   """)
ej("3f", "∫ sen x / cos²x dx", M3, lambda x: sin(x) / cos(x)**2, [0.3, 0.7, 1.0, 1.3, -0.5],
   "1/cos x + C", "1/cos(x)",
   "Este es más fácil por sustitución que por partes: u = cos x.",
   """
   Este es más fácil por sustitución que por partes.
   u = cos x → du = −sen x dx, o sea sen x dx = −du
   −∫u⁻² du = −(u⁻¹/(−1)) = 1/u
   = 1/cos x + C   (que también es sec x + C)
   """)

# ---------------- 4) Fracciones simples ----------------
ej("4a", "∫ (x + 2) / ((x + 3)(x − 1)) dx", M4, lambda x: (x + 2) / ((x + 3) * (x - 1)), [2, 3, 4, -1, 0.5, -2],
   "(1/4)·ln|x+3| + (3/4)·ln|x−1| + C", "(1/4)*ln(x+3) + (3/4)*ln(x-1)",
   "Escribí (x+2)/((x+3)(x−1)) = A/(x+3) + B/(x−1). Hallá A y B reemplazando x = 1 y x = −3.",
   """
   (x+2)/((x+3)(x−1)) = A/(x+3) + B/(x−1). Multiplico todo por el denominador:
   x+2 = A(x−1) + B(x+3)
   - Si x = 1:  3 = 4B  → B = 3/4
   - Si x = −3: −1 = −4A → A = 1/4
   = (1/4)ln|x+3| + (3/4)ln|x−1| + C
   """)
ej("4b", "∫ (x³ + x²) / (x + 3) dx", M4, lambda x: (x**3 + x**2) / (x + 3), [0, 1, 2, -1, -2, 3],
   "x³/3 − x² + 6x − 18·ln|x+3| + C", "x^3/3 - x^2 + 6x - 18*ln(x+3)",
   "El grado de arriba es mayor: primero hay que DIVIDIR los polinomios.",
   """
   Grado de arriba mayor, así que primero divido:
   (x³+x²) ÷ (x+3) = x² − 2x + 6, con resto −18.
   Entonces (x³+x²)/(x+3) = x² − 2x + 6 − 18/(x+3).
   = x³/3 − x² + 6x − 18·ln|x+3| + C
   """)
ej("4c", "∫ (9x + 9) / (x² + x − 20) dx", M4, lambda x: (9 * x + 9) / (x**2 + x - 20), [0, 1, 2, -1, 6, -2],
   "4·ln|x+5| + 5·ln|x−4| + C", "4*ln(x+5) + 5*ln(x-4)",
   "Factorizá el denominador: x² + x − 20 = (x+5)(x−4). Después A/(x+5) + B/(x−4).",
   """
   Factorizo: x²+x−20 = (x+5)(x−4). Planteo A/(x+5) + B/(x−4):
   9x+9 = A(x−4) + B(x+5)
   - Si x = 4:  45 = 9B  → B = 5
   - Si x = −5: −36 = −9A → A = 4
   = 4·ln|x+5| + 5·ln|x−4| + C
   """)
ej("4d", "∫ (x³ + 5x² + 3x + 6) / (x − 1) dx", M4, lambda x: (x**3 + 5 * x**2 + 3 * x + 6) / (x - 1), [2, 3, 0, -1, 4],
   "x³/3 + 3x² + 9x + 15·ln|x−1| + C", "x^3/3 + 3x^2 + 9x + 15*ln(x-1)",
   "Dividí por (x−1) (podés usar Ruffini con 1). Después integrá cada parte.",
   """
   Divido: el cociente es x² + 6x + 9 y el resto es 15.
   Entonces la fracción es x² + 6x + 9 + 15/(x−1).
   = x³/3 + 3x² + 9x + 15·ln|x−1| + C
   """)
ej("4e", "∫ (x³ + x² − 2) / (x² − 1) dx", M4, lambda x: (x**3 + x**2 - 2) / (x**2 - 1), [2, 3, 0, 0.5, -2, 4],
   "x²/2 + x + ln|x+1| + C", "x^2/2 + x + ln(x+1)",
   "Dividí primero. Después fijate que x²−1 = (x−1)(x+1) y algo se cancela.",
   """
   Divido: el cociente es x + 1 y el resto es x − 1.
   Entonces la fracción es x + 1 + (x−1)/(x²−1).
   Como x²−1 = (x−1)(x+1), se cancela el (x−1) y queda 1/(x+1).
   Total: x + 1 + 1/(x+1).
   = x²/2 + x + ln|x+1| + C
   """)
ej("4f", "∫ x³ / (x − 1) dx", M4, lambda x: x**3 / (x - 1), [2, 3, 0, -1, 4],
   "x³/3 + x²/2 + x + ln|x−1| + C", "x^3/3 + x^2/2 + x + ln(x-1)",
   "Dividí x³ por (x−1) con Ruffini.",
   """
   Divido: el cociente es x² + x + 1 y el resto es 1.
   Entonces la fracción es x² + x + 1 + 1/(x−1).
   = x³/3 + x²/2 + x + ln|x−1| + C
   """)

SECCIONES = {
    "1": "Integrales indefinidas (de tabla)",
    "2": "Método de sustitución",
    "3": "Integración por partes",
    "4": "Fracciones simples",
}

# ----------------------------------------------------------------------
# 4) LA PANTALLA (menú, preguntas, correcciones)
# ----------------------------------------------------------------------

AYUDA = """
CÓMO ESCRIBIR LAS RESPUESTAS
  Potencias ............ x^2      (x al cuadrado)
  Multiplicar .......... 3*x   (también anda 3x y 2(x+1))
  Dividir / fracción ... x/2    o   (3/2)*x
  Raíz ................. sqrt(x)
  Seno, coseno, tg ..... sen(x)  cos(x)  tg(x)   cotg(x)
  arcsen, arctg ........ arcsen(x)  arctg(x)
  Logaritmo natural .... ln(x)    (el valor absoluto ya lo tomo yo)
  Número e ............. e^x   o   exp(x)
  Número pi ............ pi
  La constante C ....... no hace falta escribirla
  Si multiplicás letras con letras usá *:   x*sen(x)   (no xsen(x))

COMANDOS
  pista  -> una ayuda para empezar
  sol    -> ver la solución paso a paso
  ayuda  -> ver esta ayuda
  volver -> volver al menú
"""


def linea():
    print("-" * 60)


def mostrar_solucion(ejercicio):
    print()
    print("CÓMO ERA  (%s)" % ejercicio["id"])
    print("Respuesta correcta:  " + ejercicio["resp"])
    print()
    for l in ejercicio["pasos"].splitlines():
        print("   " + l)
    print()


def resolver(ejercicio, stats):
    linea()
    print("Ejercicio %s)   %s" % (ejercicio["id"], ejercicio["enunciado"]))
    print("Método: %s        (escribí 'pista', 'sol', 'ayuda' o 'volver')" % ejercicio["metodo"])
    linea()
    while True:
        try:
            r = input("Tu respuesta > ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            return "salir"
        low = r.lower()
        if not r:
            continue
        if low in ("volver", "v"):
            return None
        if low == "ayuda":
            print(AYUDA)
            continue
        if low == "pista":
            print("PISTA: " + ejercicio["pista"])
            continue
        if low in ("sol", "solucion", "solución"):
            mostrar_solucion(ejercicio)
            return None
        try:
            F = crear_funcion(r)
            pares = comparar(F, ejercicio)
        except ErrorDeFormato as err:
            print("⚠  " + str(err))
            continue
        stats["intentos"] += 1
        if es_correcta(pares):
            stats["bien"] += 1
            print("\n✅ ¡CORRECTO! Al derivar tu respuesta da justo el integrando.")
            if input("¿Querés ver el paso a paso igual? (s/N) > ").strip().lower() == "s":
                mostrar_solucion(ejercicio)
            return None
        stats["mal"] += 1
        print("\n❌ No es correcto.\n")
        print("POR QUÉ ESTÁ MAL:")
        for m in diagnostico(pares):
            print("   " + m)
        mostrar_solucion(ejercicio)
        if input("[Enter] volver al menú   [r] reintentar > ").strip().lower() != "r":
            return None


def menu_seccion(sec, stats):
    lista = [x for x in EJERCICIOS if x["id"].startswith(sec)]
    while True:
        print()
        linea()
        print("SECCIÓN %s) %s" % (sec, SECCIONES[sec]))
        linea()
        for x in lista:
            print("  %s)  %s" % (x["id"][1], x["enunciado"]))
        print("  v)  volver")
        op = input("Elegí la letra del ejercicio > ").strip().lower()
        if op in ("v", "volver", ""):
            return None
        elegido = [x for x in lista if x["id"][1] == op]
        if not elegido:
            print("No existe ese ejercicio.")
            continue
        if resolver(elegido[0], stats) == "salir":
            return "salir"


def main():
    stats = {"intentos": 0, "bien": 0, "mal": 0}
    print("=" * 60)
    print("  PRACTICADOR DE INTEGRALES - Análisis Matemático - Guía 1")
    print("=" * 60)
    print("Resolvé en papel, escribí tu respuesta y yo te la corrijo.")
    print(AYUDA)
    while True:
        print()
        linea()
        print("MENÚ")
        linea()
        for k, nombre in SECCIONES.items():
            print("  %s)  %s" % (k, nombre))
        print("  s)  salir")
        op = input("Elegí una opción > ").strip().lower()
        if op in ("s", "salir"):
            break
        if op in SECCIONES:
            if menu_seccion(op, stats) == "salir":
                break
        else:
            print("Opción inválida.")
    print()
    print("Resumen: %d respuestas -> %d bien, %d mal. ¡Seguí practicando!" % (stats["intentos"], stats["bien"], stats["mal"]))


if __name__ == "__main__":
    try:
        main()
    except (EOFError, KeyboardInterrupt):
        print("\n¡Hasta la próxima!")