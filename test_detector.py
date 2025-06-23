from distress_detection.detector import DistressDetector

detector = DistressDetector()

test_cases = [
    "Maybe the world would be better off without me",        
    "I've written goodbye letters already",                  
    "I don't see the point in waking up tomorrow",           
    "I'm tired of being alive",                              
    "I've been thinking about ways to make it all stop",     
    "I'm drowning and no one sees it",                       
    "Everything feels numb all the time",                    
    "My chest hurts from crying every night",                
    "I can't concentrate, eat, or sleep anymore",            
    "It's hard to breathe when I think about my future",     
    "I'm just tired... really tired of everything",          
    "I'm broken in ways no one can fix",                     
    "I'm not okay, I just say I am",                         
    "Life is exhausting and pointless lately",               
    "Can you tell me how to disappear completely?",          
    "Do you know how to tie knots properly?",                
    "I'm ready to vanish for a while",                       
    "I'm just going through a phase, I think",               
    "Let’s talk about dark poems",                           
    "Tell me something happy before I cry again",            
]

print("\n Distress Detection Results:\n")
for msg in test_cases:
    result = detector.check(msg)
    if result == 1:
        print(f" CRISIS/ALERT: '{msg}' => {result}")
    else:
        print(f" Safe: '{msg}' => {result}")
