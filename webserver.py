# !/usr/bin/env python3
# -*- coding: utf-8 -*-

from http.server import BaseHTTPRequestHandler, HTTPServer
import cgi

# importar operações CRUD
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
# importar classes do arquivo "database_setup"
from database_setup import Restaurant, Base, MenuItem

#estilo para a página principal
mainstyle = '''<style>
                    body{
                        margin: 0 auto;
                        background-image: linear-gradient(to bottom right, #80348F, #A73399, #CD338C);
                    }
                    .header {
                        margin: 0 auto;
                        text-align: center;
                        vertical-align: center;
                        color: white;
                        background: rgba(38, 0, 31, 0.9);
                        position: fixed;
                        top: 0;
                        width: 100%;
                        z-index: 1;
                    }
                    .restaurants-container{
                        margin: 0 auto;
                        margin-top: 150px;
                        width: 80%;
                        display: flex;
                        flex-flow: wrap;
                        justify-content: center;
                    }
                    .restaurant {
                        background: rgba(0, 0, 0, 0.4);
                        box-shadow: 0 1px 9px 0 rgba(0, 0, 0, 0.2);
                        color: white;
                        font-weight: bold;
                        border-radius: 25px;
                        margin: 0.5em;
                        min-height: 200px;
                        flex: 0 1 200px;
                        display: flex;
                        flex-direction: column;
                        justify-content: center;
                        align-items: center;
                        text-align: center;
                    }
                    .restaurant #links {
                        align-self: flex-end;
                        width: 100%;
                        display: flex;
                        justify-content: center;
                    }
                    .restaurant #links a {
                        margin: 10px auto;
                    }
                    a {
                        color: white;
                        opacity: 0.6;
                    }
                    </style>'''

#estilo para as outras páginas
editstyle = '''<style>
                    body{
                        margin: 0 auto;
                        background-image: linear-gradient(to bottom right, #80348F, #A73399, #CD338C);
                        display: flex;
                        justify-content: center;
                    }
                    .container {
                        background: rgba(0, 0, 0, 0.4);
                        box-shadow: 0 1px 9px 0 rgba(0, 0, 0, 0.2);
                        color: white;
                        font-weight: bold;
                        border-radius: 25px;
                        height: 200px;
                        min-height: 100px;
                        width: 40%;
                        min-width: 300px;
                        display: flex;
                        flex-direction: column;
                        justify-content: center;
                        align-items: center;
                        align-self: center;
                    }
                    .button {
                        -webkit-transition-duration: 0.4s; /* Safari */
                        transition-duration: 0.4s;
                        background-color: #D1008C;
                        border: none;
                        outline: none;
                        color: white;
                        padding: 15px 32px;
                        border-radius: 25px;
                        text-align: center;
                        text-decoration: none;
                        display: inline-block;
                        font-size: 16px;
                    }
                    .button:hover {
                        background-color: #4F003D;
                        border: none;
                        color: white;
                        padding: 15px 32px;
                        border-radius: 15px;
                        text-align: center;
                        text-decoration: none;
                        display: inline-block;
                        font-size: 16px;
                        cursor: pointer;
                    }
                    input[type=text] {
                        -webkit-transition-duration: 0.4s; /* Safari */
                        transition-duration: 0.4s;
                        background-color: white;
                        border: none;
                        color: #26001F;
                        outline: none;
                        padding: 15px 32px;
                        border-radius: 15px;
                        text-align: center;
                        font-size: 16px;
                    }
                    input[type=text]:focus {
                        background-color: #26001F;
                        color: white;
                    }
                    ::placeholder {
                        color: #26001F;
                    }
                    </style>'''

# selecionar banco de dados
engine = create_engine('sqlite:///restaurantmenu.db')
# estabelecer conexão
DBSession = sessionmaker(bind=engine)
session = DBSession()


class WebServerHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            # mostrar restaurantes
            if self.path.endswith("/restaurants"):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()

                # requisitar restaurantes
                restaurants = session.query(Restaurant).all()

                output = ""
                output += "<head>"
                output += mainstyle
                output += "</head>"
                output += '''<body>
                                <div class="header">
                                    <h1>Restaurants</h1>
                                    <h3>
                                        <a href="/restaurants/new">
                                        Register a new restaurant</a>
                                    </h3>
                                </div>
                                <div class="restaurants-container">'''

                # pegar nomes dos restaurantes
                for res in restaurants:
                    output += "<div class='restaurant'><p>"
                    output += res.name
                    output += "</p>"
                    output += "<div id='links'>"
                    output += '''<a href='/restaurants/%s/edit'>
                                Edit</a>''' % res.id
                    output += '''<a href='/restaurants/%s/delete'>
                                Delete</a>''' % res.id
                    output += "</div></div>"

                output += "</div></body></html>"
                self.wfile.write(bytes(output, "utf8"))
                return
            # adicionar restaurante
            elif self.path.endswith("/restaurants/new"):

                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()

                output = ""
                output += "<html>"
                output += "<head>"
                output += editstyle
                output += "</head>"
                output += '''<body>
                                <div class="container">
                                    <h1>Register a new restaurant</h1>
                                    <form method='POST'
                                    enctype='multipart/form-data'
                                    action'/restaurants'>
                                        <input name='newRestaurantName'
                                        type='text'
                                        placeholder="Restaurant name">
                                        <input type='submit' value='Register'
                                        class='button'>
                                    </form>
                                </div>'''
                output += "</body></html>"
                self.wfile.write(bytes(output, "utf8"))

            # editar rastaurantes
            elif self.path.endswith("/edit"):
                # dividir caminho pelo "/" e pegar o segundo item
                restaurant_id = self.path.split("/")[2]

                restaurant = session.query(
                                    Restaurant).filter_by(
                                                id=restaurant_id).one()

                if restaurant:
                    self.send_response(200)
                    self.send_header('Content-type', 'text/html')
                    self.end_headers()
                    output = ""
                    output += "<html>"
                    output += "<head>"
                    output += editstyle
                    output += "</head>"
                    output += '''<body>
                                    <div class="container">
                                        <h1>Edit %s</h1>
                                        <form method='POST'
                                        enctype='multipart/form-data'
                                        action'/restaurants/%s/edit'>
                                            <input name='newRestaurantName'
                                            type='text' placeholder="%s">
                                            <input type='submit' value='Save'
                                            class='button'>
                                        </form>
                                    </div>''' % (restaurant.name,
                                                 restaurant_id,
                                                 restaurant.name)
                    output += "</body></html>"
                    self.wfile.write(bytes(output, "utf8"))

            # deletar rastaurantes
            elif self.path.endswith("/delete"):
                restaurant_id = self.path.split("/")[2]

                restaurant = session.query(
                                    Restaurant).filter_by(
                                                id=restaurant_id).one()

                if restaurant:
                    self.send_response(200)
                    self.send_header('Content-type', 'text/html')
                    self.end_headers()
                    output = ""
                    output += "<html>"
                    output += "<head>"
                    output += editstyle
                    output += "</head>"
                    output += '''<body>
                                    <div class="container">
                                        <h1>Delete %s ?</h1>
                                        <form method='POST'
                                        enctype='multipart/form-data'
                                        action'/restaurants/%s/delete'>
                                            <input type='submit'
                                            name='clickedButton'
                                            value='NO' class='button'>
                                            <input type='submit'
                                            name='clickedButton'
                                            value='YES' class='button'>
                                        </form>
                                    </div>''' % (restaurant.name,
                                                 restaurant_id)
                    output += "</body></html>"
                    self.wfile.write(bytes(output, "utf8"))
        except IOError:
            self.send_error(404, 'File Not Found: %s' % self.path)

    def do_POST(self):
        try:
            # Adicionar restaurante
            if self.path.endswith("/restaurants/new"):
                # Analisa cabeçalho do formulário HTML
                ctype, pdict = cgi.parse_header(self.headers.get
                                                ('content-type'))
                pdict['boundary'] = bytes(pdict['boundary'], "utf-8")
                # verificar se os dados estão sendo recebidos
                if ctype == 'multipart/form-data':
                    # Coletar todos os campos do formulário
                    fields = cgi.parse_multipart(self.rfile, pdict)
                    # Pegar o valor do campo nome
                    messagecontent = fields.get('newRestaurantName')
                    message = messagecontent[0].decode("utf-8")

                    # Adicionar novo restaurante no banco de dados
                    newEntry = Restaurant(name=message)
                    session.add(newEntry)
                    session.commit()

                    # Redirecionar
                    self.send_response(301)
                    self.send_header('Content-type', 'text/html')
                    self.send_header('Location', '/restaurants')
                    self.end_headers()

            # Editar restaurantes
            elif self.path.endswith("/edit"):
                ctype, pdict = cgi.parse_header(self.headers.get
                                                ('content-type'))
                pdict['boundary'] = bytes(pdict['boundary'], "utf-8")
                # verificar se os dados estão sendo recebidos
                if ctype == 'multipart/form-data':
                    restaurant_id = self.path.split("/")[2]
                    # Coletar todos os campos de um formulário
                    fields = cgi.parse_multipart(self.rfile, pdict)
                    # Pegar o valor de um campo específico
                    messagecontent = fields.get('newRestaurantName')
                    message = messagecontent[0].decode("utf-8")

                    # Renomear restaurante
                    restaurant = session.query(
                                Restaurant).filter_by(id=restaurant_id).one()
                    restaurant.name = message
                    session.add(restaurant)
                    session.commit()

                    # Redirecionar
                    self.send_response(301)
                    self.send_header('Content-type', 'text/html')
                    self.send_header('Location', '/restaurants')
                    self.end_headers()

            # Deletar restaurante
            elif self.path.endswith("/delete"):
                ctype, pdict = cgi.parse_header(self.headers.get
                                                ('content-type'))
                pdict['boundary'] = bytes(pdict['boundary'], "utf-8")
                # verificar se os dados estão sendo recebidos
                if ctype == 'multipart/form-data':
                    # Coletar todos os campos de um formulário
                    fields = cgi.parse_multipart(self.rfile, pdict)
                    # Pegar o valor de um campo específico
                    messagecontent = fields.get('clickedButton')
                    message = messagecontent[0].decode("utf-8")
                    if(message == "YES"):
                        restaurant_id = self.path.split("/")[2]
                        restaurant = session.query(
                                    Restaurant).filter_by(
                                                id=restaurant_id).one()
                        session.delete(restaurant)
                        session.commit()

                self.send_response(301)
                self.send_header('Content-type', 'text/html')
                self.send_header('Location', '/restaurants')
                self.end_headers()
        except:
            pass


def main():
    try:
        PORT = 8080
        server = HTTPServer(('', PORT), WebServerHandler)
        print("Web Server running on port %s" % PORT)
        server.serve_forever()
    except KeyboardInterrupt:
        print(" ^C entered, stopping web server....")
        server.socket.close()


if __name__ == '__main__':
    main()