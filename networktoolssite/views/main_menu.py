#!/usr/bin/env python3

from networktoolssite import networktoolssite
from flask import render_template


@networktoolssite.route('/')
@networktoolssite.route('/menu')
def index():
    return render_template('menu.html', title='Main Menu')
