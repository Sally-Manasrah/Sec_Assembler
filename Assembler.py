import sys 
import pprint
from opcode import opTable
from collections import defaultdict
def str2hex(s):
   return ''.join([('0'+hex(ord(c)).split('x')[1])[-2:] for c in s])
def fixHexString(num, limit):
   zero = "0"
   count = limit - len(num)
   num = (zero * count) + num
   return num
Symbol_Table={}
Literal_Table =defaultdict(list)
Literal_LIST=[]
def PASS_TWO(startingAddress,PROGRAMLENGTH,prog_name):
      undefined_symbol=0
      text_record_length=0
      first_objcode=str(hex(startingAddress)[2:])
      with open('Intermediate_file.mdt','r') as intermediate, open('Listing_file.txt', 'w') as Lfile,open('Object_program.txt','w+') as Object_program:
         line=intermediate.readline()
         address=line[0:4]
         previous_address=address
         OPCODE=(line[16:22]).strip()
         OPERAND=(line[23:43]).strip()
         if OPCODE =="START":
            Lfile.write(line[0:43].strip()+"\n")
            line=intermediate.readline()
            address=line[0:4]
            previous_address=address
            OPCODE=(line[16:22]).strip()
            OPERAND=(line[23:43]).strip()
         if len(hex(startingAddress)[2:]) < 6:
            startingAddress = fixHexString(str(hex(startingAddress)[2:]), 6)
         if len(PROGRAMLENGTH) < 6:
            PROGRAMLENGTH = fixHexString(PROGRAMLENGTH, 6)
         if len(prog_name) < 6:
            diff = 6 - len(prog_name)
            prog_name = prog_name + (" "* diff)            
         Object_program.write("H^"+prog_name+"^"+startingAddress+"^"+str(PROGRAMLENGTH)+"\n")
         record="T"
         text_record=""
         while OPCODE != "END":
            if not line.startswith('.'):
               if OPCODE in opTable:
                  inst_obcode=opTable[OPCODE] 
                  index = OPERAND.find(",X")
                  if index != -1:
                     temp = OPERAND[:index]
                     operand_address = Symbol_Table[temp]
                     operand_address = int(operand_address, 16)
                     operand_address += int("8000", 16)
                     operand_address = hex(operand_address)[2:]
                  else:
                     if OPERAND in Symbol_Table:
                        operand_address=Symbol_Table[OPERAND]
                     else:
                        if OPERAND in Literal_Table:
                           operand_address=str(Literal_Table[OPERAND][0])          
                        else:
                           operand_address=0
                  object_code=str(str(inst_obcode)+str(operand_address))
                  if len(object_code) < 6:
                     diff = 6 - len(object_code)
                     object_code = object_code + ("0"* diff)
               else:
                  if OPCODE == "WORD":
                     OPERAND = hex(int(OPERAND))[2:]
                     OPERAND = fixHexString(OPERAND,6)
                     object_code = OPERAND
                  elif OPCODE == "BYTE":
                     if OPERAND[0] == 'C':
                        operand_address= str2hex(OPERAND[2:-1])
                     elif OPERAND[0] == 'X':
                        OPERAND = OPERAND[2:-1]
                        operand_address = OPERAND
                     object_code = operand_address
                  elif OPCODE=="RESW" or "RESB":
                     object_code="None"
               object_code_length=round(len(object_code)*0.5)
               difference=int(address,16)-int(previous_address,16)
               available_size=30-text_record_length 
               if available_size<object_code_length or(difference>40):
                  if len(str(text_record_length)) < 2:
                     text_record_length = fixHexString(text_record_length, 2)
                  text_record_str=hex(text_record_length)[2:]+text_record
                  if(len(first_objcode))< 6:
                     diff = 6 - len(str(first_objcode))
                     first_objcode=("0"* diff)+str(first_objcode)
                  Object_program.write(record+"^"+first_objcode+"^"+text_record_str+"\n")
                  if (difference<40):
                     first_objcode=int(first_objcode,16)
                     first_objcode+=int(text_record_str[0:2],16)
                     first_objcode=hex(first_objcode)[2:]
                  else:
                     first_objcode=hex(int(address,16))[2:]
                  text_record_length=0
                  text_record=""
               if object_code!="None":
                     text_record+="^"+object_code 
                     text_record_length+=object_code_length              
               else:
                  text_record=text_record
                  object_code=""
            if OPERAND:
               op_len=len(line[23:43].strip())
               if op_len < 19 :
                  diff = 19 - op_len
                  l=(" "* diff)
            else:
               l="                      "
            Lfile.write(line[0:43].strip()+l+object_code+"\n")
            line=intermediate.readline()
            previous_address=address
            address=line[0:4]
            OPCODE=(line[16:22]).strip()
            OPERAND=(line[23:43]).strip()
         text_record_length=str(hex(text_record_length)[2:])
         if len(str(text_record_length)) < 2:
            text_record_length = fixHexString(str(text_record_length), 2)
         if(len(first_objcode))< 6:
                     diff = 6 - len(str(first_objcode))
                     first_objcode=("0"* diff)+str(first_objcode)
         Object_program.write(record+"^"+first_objcode+"^"+text_record_length+text_record)
         Object_program.write("\n"+"E^"+startingAddress)
         Lfile.write(line[0:43].strip()+"\n")  



#THIS IS PASS ONE FUNCTION 
def PASS_ONE():
   lineno=1
   noName=0
   with open("Example3.txt") as source, open('Intermediate_file.mdt', 'w+') as intermediate:
      line=source.readline()
      LABEL=(line[0:9]).strip()
      if not LABEL:
            noName=1     
      OPCODE=(line[10:16]).strip()
      OPERAND=(line[17:36]).strip()
      if OPCODE =="START":
         startingAddress=int(OPERAND,16)
         LOCCTR=startingAddress
         intermediate.write(str(hex(LOCCTR)[2:])+"   "+line)
         Symbol_Table[LABEL]=hex(LOCCTR)[2:]
         line=source.readline()
         lineno +=1
         LABEL=(line[0:9]).strip()
         OPCODE=(line[10:16]).strip()
         OPERAND=(line[17:36]).strip()
      else:
         startingAddress=0
         LOCCTR=0
      while OPCODE != "END":
         LABEL=(line[0:9]).strip()
         OPERAND=(line[17:36]).strip()
         if not line.startswith('.'):
            if len(str(LOCCTR))<4:
               diff = 4 - len(str(LOCCTR))
               LOCCTR=("0"* diff)+str(LOCCTR)
               intermediate.write(str(LOCCTR)+"   "+line)
               LOCCTR=int(LOCCTR)
            else:
               intermediate.write(str(hex(LOCCTR)[2:])+"   "+line)
            if LABEL:
               if LABEL in Symbol_Table :
                  sys.exit("!DUPLICATE LABEL\n"+LABEL+" "+"Line"+" "+str(lineno)+" "+"is already exist in SymbolTable")
               else:
                  Symbol_Table[LABEL]=hex(LOCCTR)[2:]
            if OPCODE == "LTORG":
               for i in Literal_LIST:
                  if i not in Literal_Table:
                     Literal_Table[i].append(hex(LOCCTR)[2:] )
                     if i[1:2]=='X':
                        Literal_Table[i].append(round(len(i[3:-1])*0.5))
                     else:
                        Literal_Table[i].append(len(i[3:-1]))
                     Literal_Table[i].append(str2hex(i[3:-1]))
                     LOCCTR+=len(i[3:-1].strip())
                     Literal_LIST.remove(i)
            else:
               if OPCODE in opTable:
                  LOCCTR += 3
               else:
                  if OPCODE == "WORD":
                     LOCCTR +=3
                  else:
                     if OPCODE == "RESW":
                        LOCCTR += 3*int(OPERAND.strip())
                     else:
                        if OPCODE == "RESB":
                           LOCCTR += int(OPERAND.strip())
                        else:
                           if OPCODE== "BYTE":
                              if OPERAND.startswith('C'):
                                 LOCCTR+=len(OPERAND[2:-1].strip())
                              else:
                                 if OPERAND.startswith('X'):
                                    LOCCTR+=(round(len(OPERAND[2:-1])*0.5))
                                 else:
                                    LOCCTR +=len(OPERAND.strip())
                           else:
                              sys.exit("!INVALID OPCODE\n"+OPCODE+" "+"Line"+" "+str(lineno)+" "+"is not valid ")
            if OPERAND.startswith("="):
               if OPERAND not in Literal_LIST:
                  Literal_LIST.append(OPERAND)
         line=source.readline()
         lineno +=1
         OPCODE=(line[10:16]).strip()
      for i in Literal_LIST:
         if i != Literal_LIST[-1]:
            Literal_Table[i].append(hex(LOCCTR)[2:])
            if i[1:2]=='X':
                Literal_Table[i].append(round(len(i[3:-1])*0.5))
                Literal_Table[i].append(i[3:-1])
                LOCCTR+=(round(len(i[3:-1])*0.5))
            else:
               Literal_Table[i].append(len(i[3:-1]) )
               Literal_Table[i].append(str2hex(i[3:-1]) )
               LOCCTR +=len(i[3:-1].strip())
               Literal_Table[i].append(str2hex(i[3:-1]))
               LOCCTR+=(round(len(i[3:-1])*0.5))
         else:
            Literal_Table[i].append(hex(LOCCTR)[2:] )
            if i[1:2]=='X':
               Literal_Table[i].append(round(len(i[3:-1])*0.5))
               Literal_Table[i].append(i[3:-1])
            else:
               Literal_Table[i].append(len(i[3:-1]))
               Literal_Table[i].append(str2hex(i[3:-1]))
      if len(str(LOCCTR))<4:
         diff = 4 - len(str(LOCCTR))
         LOCCTR=("0"* diff)+str(LOCCTR)
         intermediate.write(str(LOCCTR)+"   "+line)
         LOCCTR=int(LOCCTR)
      else:
         intermediate.write(str(hex(LOCCTR)[2:])+"   "+line)         
      intermediate.close()
      if noName == 1:
         prog_name="Unnamed_program"
      else:
         prog_name= str(next(iter(Symbol_Table)))
      PROGRAMLENGTH=hex(LOCCTR-startingAddress)[2:] 
      print("\n"+"Program name is : " +prog_name+"\n")
      print("Location Counter is "+str(hex(LOCCTR)[2:])+"\n")
      print("PROGRAM LENGTH is "+str(PROGRAMLENGTH)+"\n")
      print("Symbol_Table is")
      pprint.pprint(Symbol_Table)
      print("\n"+"Literal_Table is ")
      pprint.pprint(dict(Literal_Table))
      PASS_TWO(startingAddress,PROGRAMLENGTH,prog_name)
PASS_ONE()
   
   
 