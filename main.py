import discord
from settings import settings1
from discord.ext import commands
import sympy as sp
import aiohttp
import os
import matplotlib.pyplot as plt
from io import BytesIO
from PIL import Image, ImageOps
import numpy as np
from sympy import simplify, solve, symbols, Eq, diff
import openai
from openai.error import RateLimitError

# Crear una instancia de bot
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'Conectado como {bot.user}')

@bot.command()
async def resolver(ctx, *, problema: str):

    try:
        x, y, z = symbols('x y z')  # Define variables comunes
        if '=' in problema:  # Resolver ecuaciones
            lado_izq, lado_der = problema.split('=')
            ecuacion = Eq(simplify(lado_izq), simplify(lado_der))
            solucion = solve(ecuacion)
            pasos = f"Ecuación: {ecuacion}\nSolución: {solucion}"
        else:  # Simplificar expresiones
            resultado = simplify(problema)
            expandido = resultado.expand()  # Asegura la expansión completa
            pasos = f"Expresión simplificada: `{resultado}`\nExpresión expandida: `{expandido}`"

        await ctx.send(f"**Problema:** `{problema}`\n**Solución paso a paso:**\n{pasos}")

    except Exception as e:
        await ctx.send(f"Hubo un error al resolver el problema: {str(e)}")

@bot.command(name='graficar')
async def graficar(ctx, funcion: str):
    """
    Comando para graficar funciones matemáticas y dar información analítica.
    """
    try:
        # Variables simbólicas
        x = symbols('x')

        # Convertir la función de texto a una expresión evaluable
        expr = eval(funcion)  # Convertir la función a una expresión simbólica

        # Cálculo del vértice (si es una parábola)
        derivada = diff(expr, x)  # Derivada de la función
        x_vertice = solve(derivada, x)  # Encontrar x donde la derivada es 0 (vértice)
        if x_vertice:  # Si se encuentra vértice
            y_vertice = expr.subs(x, x_vertice[0])
            vertice = (x_vertice[0], y_vertice)
        else:
            vertice = "No aplica"

        # Calcular raíces (intersección con el eje X)
        raices = solve(expr, x)

        # Intersección con el eje Y (x = 0)
        interseccion_y = expr.subs(x, 0)

        # Crear datos para graficar
        x= np.linspace(-10, 10, 500)
        y= [eval(funcion.replace('x', f'({xi})')) for xi in x]

# Crear el gráfico
        plt.plot(x, y, label='parabola', color='green')
        plt.title(f'Gráfica de {funcion}')
        plt.xlabel('Eje X')
        plt.ylabel('Eje Y')
        plt.axhline(0, color='black', linewidth=0.8)
        plt.axvline(0, color='black', linewidth=0.8)
        plt.grid(color='gray', linestyle='--', linewidth=0.5)
        plt.legend()

        # Guardar la gráfica como imagen
        filename = 'grafica.png'
        plt.savefig(filename)
        plt.close()
        # Enviar la información y el gráfico al canal
        await ctx.send(f"Función graficada: {funcion}\nAnálisis:\n- Vértice: {vertice}\n- Raíces: \nIntersección con X: {raices}\nIntersección con Y: {interseccion_y}")
        await ctx.send(file=discord.File(filename))

    except Exception as e:
        await ctx.send(f"Error al procesar la función: {str(e)}")

@bot.command()
async def hello(ctx):
    await ctx.send(f'Hi! I am a bot {bot.user}!')

@bot.command()
async def check(ctx, link=None):
    if ctx.message.attachments:  # Manejo de archivos adjuntos
        for attachment in ctx.message.attachments:
            file_name = attachment.filename
            file_url = attachment.url
            await attachment.save(f"./{file_name}")
            await ctx.send(f"Guardé la imagen en ./{file_name}")
    elif link:  # Manejo de enlaces proporcionados como argumento
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(link) as response:
                    if response.status == 200:
                        content_disposition = response.headers.get("Content-Disposition", "")
                        file_name = (
                            content_disposition.split("filename=")[-1].strip('"')
                            if "filename=" in content_disposition
                            else os.path.basename(link)
                        )
                        file_path = f"./{file_name}"
                        with open(file_path, "wb") as f:
                            f.write(await response.read())
                        await ctx.send(f"Guardé el archivo del enlace en {file_path}")
                    else:
                        await ctx.send(f"No se pudo descargar el archivo. Estado HTTP: {response.status}")
            except Exception as e:
                await ctx.send(f"Hubo un error al descargar el archivo: {e}")
    else:
        await ctx.send("Por favor, sube una imagen o proporciona un enlace.")

openai.api_key = 'API KEY'

try:
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user", "content": "write a haiku about ai"}])
except RateLimitError:
    print("Has excedido tu cuota actual de uso de la API. Por favor, verifica tu plan y detalles de facturación.")

bot.run(settings1["TOKEN"])
