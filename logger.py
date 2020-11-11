
global m_blnDebug
m_blnDebug = False

# Print str_msg with a DEBUG: tag.
def debug(str_msg):
    global m_blnDebug
    if(m_blnDebug == True):
        print("DEBUG: " + str(str_msg))


# Toggle debug printing.
def setDebug(bln_debug):
    global m_blnDebug
    m_blnDebug = bln_debug