import functions as fn

# creating something to give me option of what I want to choose
choices = []

userchoices = {1: """Test onevidonegif:
               Create one gif with one YouTube URL input""",
               2: """Test onegifpervid:
               Create one gif per YouTube URL input with many start/stop
               times""",
               3: """Test manygifpervid:
               Create many gifs per YouTube URL with many start/stop
               times, each start/stop time will create one gif""",
               4: "Run All Functions"}

for i in userchoices:
    print(str(i) + ": " + userchoices[i])
    choices.append(i)
choice = input("Select a number: ")

# Link of video to download
link = 'https://www.youtube.com/watch?v=9Im-PIs-Ki0'
link2 = 'https://www.youtube.com/watch?v=Gsk6pLLcIFI'
link3 = 'https://www.youtube.com/watch?v=DNQ2CHEL3Tw'

# data structure to make some functions work
test1 = {link: {'start': ['00:00:09.00', '00:00:15.90'],
                'end': ['00:00:11.50', '00:00:18.30']},
         link2: {'start': ['00:00:09.00', '00:00:15.90'],
                 'end': ['00:00:11.50', '00:00:18.30']}}

test2 = {link3: {'start': ['00:00:09.00', '00:00:15.90'],
                 'end': ['00:00:11.50', '00:00:18.30']}}

if choice == '1':
    fn.onevidonegif(link3, '00:00:00.00', '00:00:05.00')

elif choice == '2':
    fn.onegifpervid(test1)

elif choice == '3':
    fn.manygifpervid(test1)

elif choice == '4':
    print("Testing onevidonegif")
    fn.onevidonegif(link3, '00:00:00.00', '00:00:05.00')
    print("Testing onegifpervid")
    fn.onegifpervid(test1)
    print("Testing manygifpervid")
    fn.manygifpervid(test1)
