from flask import Blueprint,Flask, render_template, jsonify, request
from functools import wraps
from flask_cors import CORS
import pandas as pd



rotasPlataformaWeb = Blueprint('rotasPlataformaWeb', __name__)

@rotasPlataformaWeb.route('/')
def home():
    return render_template('index.html')
@rotasPlataformaWeb.route('/TelaEstrutura')
def telaEstrutura():
    return render_template('TelaEstrutura.html')
@rotasPlataformaWeb.route('/TelaPlano')
def TelaPlano():
    return render_template('TelaPlano.html')
@rotasPlataformaWeb.route('/TelaPrincipal')
def TelaPrincipal():
    return render_template('TelaPrincipal.html')
@rotasPlataformaWeb.route('/TelaUsuarios')
def TelaUsuarios():
    return render_template('TelaUsuarios.html')
@rotasPlataformaWeb.route('/TelaCurva')
def TelaCurvaABC():
    return render_template('TelaCurva.html')