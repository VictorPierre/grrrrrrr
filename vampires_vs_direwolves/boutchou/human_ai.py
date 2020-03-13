from boutchou.abstract_ai import AbstractAI
from flask import Flask, render_template, request
from threading import Thread
import os
from time import sleep


class HumanAI(AbstractAI):

    def __init__(self):
        super().__init__()
        #create web app
        self.__create_web_app()
        #Lauch web app
        server = Thread(target=self.app.run)
        server.start()

        self._move_is_ready = False
        self.moves=[]

    def __create_web_app(self):
        template_dir = os.path.abspath('../web_interface')
        self.app = Flask(__name__, template_folder=template_dir, static_folder=template_dir+'/static',)
        
        @self.app.route('/')
        def index():
            return render_template('index.html', map = self._map)
        
        @self.app.route('/load_map')
        def load_map():
            return render_template('map.html', map = self._map, specie = self._species.to_string())

        @self.app.route('/submit', methods = ['POST'])
        def submit():
            self._move_is_ready = True
            data = request.get_json()
            self.moves = [tuple(x) for x in data["moves"]]
            return 'ok'
        

    def generate_move(self):
        self._move_is_ready = False
        self.moves=[]
        print('Waiting for a move')
        while not self._move_is_ready:
            sleep(1)
        return self.moves
