# !/usr/bin/env python3
# -*- coding: utf-8 -*-

from http.server import BaseHTTPRequestHandler, HTTPServer

# importar operações CRUD
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
# importar classes do arquivo "database_setup"
from database_setup import Restaurant, Base, MenuItem

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
                output += "</head>"
                output += '''<body>
                                <div class="header">
                                    <h1>Restaurants</h1>
                                    <h3>
                                        <a href="#">
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
                    output += '''<a href='#'>
                                Edit</a>''' 
                    output += '''<a href='#'>
                                Delete</a>''' 
                    output += "</div></div>"

                output += "</div></body></html>"
                self.wfile.write(bytes(output, "utf8"))
                return
        except IOError:
            self.send_error(404, 'File Not Found: %s' % self.path)

    def do_POST(self):
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
