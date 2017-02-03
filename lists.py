from pick import pick
example = [['one', 'two'] for __ in xrange(4)]
if example[0][1] == 'two':
    print example
else:
    print 'not found'
if 'true' is 'true':
    print 'true' + ' that'


class Hitchhiker:
    def __init__(self, name='Samy'):
        self.name = name

    def get_hiker(self):
        return self.name

hitchhiker = Hitchhiker()
print hitchhiker.get_hiker()
title = 'Please choose your favorite programming language: '
options = ['Java', 'JavaScript', 'Python', 'PHP', 'C++', 'Erlang', 'Haskell']
option, index = pick(options, title)
print index