def supertrend(statsdf,period, multiplier):
    st = 'st_' + str(period) + '_' + str(multiplier)
    # Compute basic upper and lower bands
    statsdf['basic_ub'] = (statsdf['high'] + statsdf['low']) / 2 + multiplier * statsdf['atr']
    statsdf['basic_lb'] = (statsdf['high'] + statsdf['low']) / 2 - multiplier * statsdf['atr']
    print(statsdf.head(1))
    # Compute final upper and lower bands
    for i in range(0, len(statsdf)):
        if i < period:
            statsdf.ix[i,'basic_ub'] = 0.00
            statsdf.ix[i,'basic_lb'] = 0.00
            statsdf.ix[i,'final_ub'] = 0.00
            statsdf.ix[i,'final_lb'] = 0.00
           
        else:
            statsdf.ix[i,'final_ub'] = (statsdf.ix[i,'basic_ub']
                                         if statsdf.ix[i,'basic_ub'] < statsdf.ix[i-1,'final_ub'] or statsdf.ix[i-1,'close'] > statsdf.ix[i-1,'final_ub']
                                         else statsdf.ix[i-1,'final_ub'])
            
            statsdf.ix[i,'final_lb'] = (statsdf.ix[i,'basic_lb']
                                         if statsdf.ix[i,'basic_lb'] > statsdf.ix[i-1,'final_lb'] or statsdf.ix[i-1,'close'] < statsdf.ix[i-1,'final_lb'] 
                                         else statsdf.ix[i-1,'final_lb'])

    # Set the Supertrend value
    for i in range(0, len(statsdf)):
        if i < period:
            statsdf.ix[i,st] = 0.00
            
        else:
            statsdf.ix[i,st] = (statsdf.ix(i, 'final_ub')
                                 if ((statsdf.ix[i-1, st] == statsdf.ix[i-1, 'final_ub']) and (statsdf.ix[i, 'close'] <= statsdf.ix[i, 'final_ub']))
                                 else (statsdf.ix[i, 'final_lb']
                                       if ((statsdf.ix[i-1, st] == statsdf.ix[i-1, 'final_ub']) and (statsdf.ix[i, 'close'] > statsdf.ix[i, 'final_ub']))
                                       else (statsdf.ix[i, 'final_lb']
                                             if ((statsdf.ix[i-1, st] == statsdf.ix[i-1, 'final_lb']) and (statsdf.ix[i, 'close'] >= statsdf.ix[i, 'final_lb']))
                                             else (statsdf.ix[i, 'final_ub']
                                                   if((statsdf.ix[i-1, st] == statsdf.ix[i-1, 'final_lb']) and (statsdf.ix[i, 'close'] < statsdf.ix[i, 'final_lb']))
                                                   else 0.00
                                                  )
                                            )
                                      ) 
                                )
                                              