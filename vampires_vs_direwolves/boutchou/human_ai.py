from boutchou.abstract_ai import AbstractAI


class HumanAi(AbstractAI):

    def generate_move(self):

        moves = []
        species_positions = self._map.find_species_position(self._species)
        old_position = species_positions[0]
        number = self._map.get_cell_species_count(old_position, self._species)
        if not species_positions:
            return None
        print(f"you have {number} units in {old_position}")
        while True:

            stri = input('type move here \n')
            if stri == 'end':
                break
            else:
                try:
                    move = tuple(map(int, stri.split(' ')))
                    moves.append(move)
                    assert len(move) == 5
                except Exception as e:
                    print(e)
                    print('a move is composed of 5 integers')
                    print('to finish playing type end')
        if not moves:
            moves = [(*old_position, number, *old_position)]
        print(moves)
        return moves
