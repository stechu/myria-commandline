worker_2 = '''
R = scan(chushumo:worker_2:twitter_1m);
-- query(x,y,z,p):-R(x,y),S(y,z),T(z,x)
query = [from R, R as S, R as T
       where R.$1 = S.$0 and
             S.$1 = T.$0 and
             T.$1 = R.$0
       emit R.$0 as x, S.$0 as y, S.$1 as z];
store(query,chushumo:worker_2:triangle);
'''

worker_4 = '''
R = scan(chushumo:worker_4:twitter_1m);
-- query(x,y,z,p):-R(x,y),S(y,z),T(z,x)
query = [from R, R as S, R as T
       where R.$1 = S.$0 and
             S.$1 = T.$0 and
             T.$1 = R.$0
       emit R.$0 as x, S.$0 as y, S.$1 as z];
store(query,chushumo:worker_4:triangle);
'''

worker_8 = '''
R = scan(chushumo:worker_8:twitter_1m);
-- query(x,y,z,p):-R(x,y),S(y,z),T(z,x)
query = [from R, R as S, R as T
       where R.$1 = S.$0 and
             S.$1 = T.$0 and
             T.$1 = R.$0
       emit R.$0 as x, S.$0 as y, S.$1 as z];
store(query,chushumo:worker_8:triangle);
'''

worker_16 = '''
R = scan(chushumo:worker_16:twitter_1m);
-- query(x,y,z,p):-R(x,y),S(y,z),T(z,x)
query = [from R, R as S, R as T
       where R.$1 = S.$0 and
             S.$1 = T.$0 and
             T.$1 = R.$0
       emit R.$0 as x, S.$0 as y, S.$1 as z];
store(query,chushumo:worker_16:triangle);
'''

worker_32 = '''
R = scan(chushumo:worker_32:twitter_1m);
-- query(x,y,z,p):-R(x,y),S(y,z),T(z,x)
query = [from R, R as S, R as T
       where R.$1 = S.$0 and
             S.$1 = T.$0 and
             T.$1 = R.$0
       emit R.$0 as x, S.$0 as y, S.$1 as z];
store(query,chushumo:worker_32:triangle);
'''
