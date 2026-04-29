from 
t1=Table(name='demo',columns=['pt'],rows=['age'])#,'high_risk_condition_abbr_list'])
t2=Table(name='tab_dx',columns=['screened','selected','enrolled'],rows=['t2d_icd','hba1c_loinc','metformin_rxnorm'])
tab=t2.compute_tab()
tab.to_excel(f"tab2.xlsx")