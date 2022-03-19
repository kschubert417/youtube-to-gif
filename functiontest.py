import functions as fn
import os

print(os.path.join(os.getcwd(), "media", "output"))
print(os.path.exists(os.path.join(os.getcwd(), "media", "output")))

fn.deleteoldfiles([os.path.join(os.getcwd(), "media", "output")])
