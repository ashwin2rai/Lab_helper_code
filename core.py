import pandas as pd

class synchDICInstron:
    """
    Class synchs DIC and Instron CSVs. Assumes all times in CSVs are in seconds.
    If synchronization functions returns errors, header locations for CSVs have to specified explicitely. 
    This can be entered in the writetoCSV method, as:
    writetoCSV(filename,Instronheader=17,DIC_header=3),
    where Instronheader is the row of the header of the Instron CSV table
    and DIC_header is the row of the header of the DIC CSV table
    """
    def __init__(self,DIC_file,Instron_file,date):
        self.DIC_file = DIC_file
        self.Instron_file = Instron_file
        self.date = date
    
    def preProcInstron(self,header_var):
        if header_var is None:
            with open(self.Instron_file) as file:
                temp_var = file.read()
            self.header_sp = temp_var[0:temp_var.find('Load')+1].count('\n')
            del(temp_var)
        else:
            self.header_sp = header_var-1
        
        inst_dat=pd.read_csv(self.Instron_file,header=self.header_sp)
        inst_dat.columns=pd.read_csv(self.Instron_file,header=self.header_sp-1,nrows=2).columns
        inst_dat.index=pd.to_datetime(inst_dat['Time'],unit='s',origin=pd.Timestamp(self.date))
        del(inst_dat['Time'])
        
        inst_dat['Load']=pd.to_numeric(inst_dat['Load'].str.replace(',', ''),errors='coerce')
        inst_dat['Load'] = inst_dat['Load'] -inst_dat['Load'][0]
        inst_dat['Extension']=inst_dat['Extension']-inst_dat['Extension'][0]
        
        self.inst_dat=inst_dat.resample('s').ffill()
        return self
        
    def preProcDIC(self,DIC_header):
        dic_dat=pd.read_csv(self.DIC_file,header=DIC_header)
        dic_dat.columns=dic_dat.columns.str.strip()
        dic_dat.index=pd.to_datetime(dic_dat['Time [s]'],unit='s',origin=pd.Timestamp(date))
        del(dic_dat['Time [s]'])
        
        self.dic_dat=dic_dat.resample('s').ffill()
        return self
    
    def writetoCSV(self,ffname,Instronheader=None,DIC_header=3):
        self.preProcInstron(Instronheader)
        self.preProcDIC(DIC_header-1)
        pd.concat([self.inst_dat,self.dic_dat],axis=1).reset_index().to_csv(ffname,sep=',')
        
            


date = '2019-06-07'
final_filename='synchedfile.csv'
DIC_file='DIC_straindata06072019_7.csv'
Instron_file='Instron_06072019_7.csv'


synchFile=synchDICInstron(DIC_file,Instron_file,date)
synchFile.writetoCSV(final_filename)
