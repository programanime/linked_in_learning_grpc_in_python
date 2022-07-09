from time import sleep

def rand_events(count):
    for number in range(count):
        yield {"number":number}
        sleep(1)

for x in rand_events(10):
    print(x)


