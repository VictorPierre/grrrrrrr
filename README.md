# Projet CS IA : grrrrrrr

## Requirements
Python 3.6+ must be installed. 
We assume it can be accessed by `python` command, 
but on linux distribution, it is more likely to be
`python3`.

To install package requirements, run the following command lines:
```
cd vampires_vs_direwolves
python -m pip install -r requirements.txt ou conda install -–yes -–file requirements.txt 
```

## How to run grrrrrrr with its terrible AI Boutchou ?
```
cd vampires_vs_direwolves
python main.py [HOST_IP] [PORT]
```

If host ip and port are not specified, default values in 
`server_connection/config_connection.py` are used.


## Project structure
```
.
├── doc/                                           << Documentation
├── graphic_interface/                             << Interface graphique et serveur de jeu (Windows) 
├── map_generator/                                 << Générateur aléatoire de cartes (Windows)
├── vampires_vs_direwolves/                        << Projet Python
│   ├── alphabeta/                                 <== Implémentation d'Alpha-Beta et heuristiques           
│   │   ├── __init__.py                            
│   │   ├── abstract_heuristic.py                  
│   │   ├── abstract_possible_moves_computer.py    
│   │   ├── alphabeta.py                           
│   │   ├── group_heuristics.py                    
│   │   └── simple_heuristics.py                   
│   ├── battle_computer/                           
│   │   └── __init__.py                            
│   │   ├── battle_computer.py                     
│   ├── boutchou/                                  <== Package des IA, nom de code: boutchou
│   │   ├── __init__.py                            
│   │   ├── abstract_ai.py                         
│   │   ├── alpha_beta_ai.py                       <-- IA implémentant l'algorithme Alpha-Beta
│   │   ├── boutchou_ai.py                         <-- IA finale
│   │   ├── human_ai.py                            <-- Jeu par un humain sur l'interface web
│   │   ├── multi_split_ai.py                      <-- Jeu avec séparation en multitude de groupes
│   │   ├── random_ai.py                           <-- Jeu aléatoire
│   │   ├── rules.py                               
│   │   ├── rules_sequence.py                      
│   │   ├── rush_to_humans_ai.py                   <-- IA utilisant des règles simples
│   │   ├── rush_to_opponent_ai.py                 <-- IA utilisant des règles simples
│   │   └── tkinter_ai.py                          <-- Jeu par un humain sur l'interface tkinter
│   ├── common/                                    <== Package d'utilitaires communs
│   │   ├── __init__.py                            
│   │   ├── exceptions.py                          
│   │   ├── logger.py                              
│   │   ├── models.py                              
│   │   └── xml_map_parser.py                      
│   ├── game_management/                           <== Package qui gère le jeu
│   │   ├── __init__.py                            
│   │   ├── abstract_game_map.py                   
│   │   ├── abstract_game_map_with_visualizer.py   
│   │   ├── game_manager.py                        <-- Gestionnaire de jeu client
│   │   ├── game_map.py                            <-- Implémentation de la carte de jeu
│   │   ├── game_master.py                         <-- Gestionnaire de jeu maître alternatif (multi-plateforme)
│   │   ├── game_monitoring.py                     
│   │   ├── map_helpers.py                         
│   │   ├── map_viewer.py                          <-- Visualiseur de jeu alternatif tkinter (multi-plateforme)
│   │   ├── rule_checks.py                         
│   │   └── server_game_map.py                     
│   ├── server_connection/                         <== Serveur client
│   │   ├── client.py                              
│   │   ├── config_connection.py                   <-- Configuration des adresses et ports par défaut  
│   │   ├── game_server.py                         <-- Serveur de jeu alternatif (multi-plateforme)
│   │   └── server_models.py                       
│   ├── tests/                                     <== Tests
│   │   ├── __init__.py                            
│   │   ├── test_maps/                             
│   │   ├── generate_game_maps.py                  
│   │   └── test_multiple_games.py                 
│   ├── launch_game.py                             
│   └── main.py                                    <== Programme principal pour le tournoi
├── web_interface/                                 << Serveur web pour jouer manuellement (utiliser l'"IA" HumanAI) 
│   ├── index.html                                 
│   ├── map.html                                   
│   └── static                                     
│       ├── index.css                              
│       └── index.js                               
├── README.md                                      
└── requirements.txt                               
```                                                
