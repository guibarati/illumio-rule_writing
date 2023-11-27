import json,openpyxl,os,code,sys
#code.interact(local=dict(globals(),**locals()))
file_info = ''


def help():
    print('save() -> saves the information for file name and folder location')
    print('load_file_info() -> loads file name and folder information')
    print('load_file() -> loads excel file into variable')
    print('mergeDictionary(dict_1,dict_2) -> merge dictionaries adding values to a list')
    print('merge_lines() -> receives the fields that rules should be merged by and merges excel rows into list of dictionaries')



def save():
    global file,folder
    data = {}
    data['file'] = file
    data['folder'] = folder
    #os.chdir(os.path.dirname(sys.argv[0]))
    abspath = os.path.abspath(__file__)
    dname = os.path.dirname(abspath)
    os.chdir(dname)
    with open('file_info.json','w') as f:
        json.dump(data, f)
def lf():
    load_file_info()

def load_file_info():
    global file_info
    file_info = {}
    with open('file_info.json','r') as f:
        file_info = json.load(f)


def load_file():
    global file,folder,file_info
    if file_info != '':
        file = file_info['file']
        folder = file_info['folder']
        print('Working with file information:')
        print('File: ' + file)
        print('Folder: ' + folder)
        sheetname = input('Enter the Excel sheet name (Note: This name is case sensitive!): ')

    if file_info == '':    
        file = input('Enter the Excel file name with the updated attributes (Example - file.xlsx): ') #'_macropt.xlsm' 
        folder = input('Enter the folder path where the Excel file is located (Example - c:\sample): ') #r'C:\Users\gui.barati\OneDrive - Illumio\Documents\Clients\TeamHealth\Excel Data' #
        sheetname = input('Enter the Excel sheet name (Note: This name is case sensitive!): ')
    os.chdir(folder)
    wb = openpyxl.load_workbook(file)
    sheet = wb[sheetname]
    return(sheet)

def mergeDictionary(dict_1, dict_2):
   dict_3 = {**dict_2, **dict_1}
   for key, value in dict_3.items():
       if 'list' in str(type(dict_3[key])):
           if key in dict_1 and key in dict_2:
               if dict_2[key] not in dict_3[key]:
                   dict_3[key].append(dict_2[key]) 
       else:
           if key in dict_1 and key in dict_2:
               if value != dict_2[key]:
                   dict_3[key] = [value , dict_2[key]] 
   return dict_3

def merge_lines():
    sheet = load_file()
    fields = []
    lines = []
    mlines = []
    for j in range(1,sheet.max_column+1):
        fields.append(sheet.cell(1,j).value)
        if 'Protocol' in sheet.cell(1,j).value:
            proto_col = j
        if 'Port' in sheet.cell(1,j).value:
            port_col = j    
    for i in range(2,sheet.max_row+1):
        line = {}
        for j in fields:
            if fields.index(j)+1 not in [proto_col,port_col]:
                line[j] = sheet.cell(i,fields.index(j)+1).value
            if fields.index(j)+1 == port_col:
                line[j] = {'port':sheet.cell(i,fields.index(j)+1).value,'proto':sheet.cell(i,proto_col).value}
        lines.append(line)
    if 'Port' in lines and 'Protocol' not in lines:
        print('Ports are present but the Protocol column is missing')
        return
    print('Merge rules by:')
    for i in fields:
            if i != 'Protocol':
                print(' ',i)
    mergeby = []
    print(' ')
    nf = 'a'
    while nf.lower() != 'q':
        nf = input('Enter field to merge rules by. Enter "q" to finish: ')
        if nf not in fields and nf.lower() != 'q':
            print('Field not found. Fields are case sensitive')
            print('')
        if nf in fields:
            mergeby.append(nf)
    skipline = []
    #print('Cells with the "Ignore Content" value on the "Merge By" cell will not be merged')
    #print('even if they have the same content. E.g. "blank"')
    ignore_content = '(blank)' #input('Ignore content: ')
    for i in range(len(lines)):
        for j in range(i+1,len(lines)):
            if j not in skipline:
                merge = []
                if len(mergeby) > 0:
                    for k in mergeby:
                        #if ignore_content not in lines[i][k]:
                        if lines[i][k] == lines[j][k] and lines[i][k] != ignore_content:
                            merge.append('y')
                        if lines[i][k] != lines[j][k]:
                            merge.append('n')
                    if 'n' not in merge and 'y' in merge:
                        lines[i] = mergeDictionary(lines[i],lines[j])
                        skipline.append(j)
    for i in lines:
        for j in i:
            if 'list' not in str(type(i[j])):
                i[j] = [i[j]]
            
    for i in range(0,len(lines)):
        if i not in skipline:
            mlines.append(lines[i])
    return(mlines)
