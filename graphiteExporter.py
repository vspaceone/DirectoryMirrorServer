import graphyte

graphyte.init('localhost', prefix='system.sync')
graphyte.send('foo.bar', 50)
