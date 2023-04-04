import time
from modbusBatch.mbBatch import MbBatch
mb = MbBatch(host="192.168.1.95",
             port=502,
             retry=3,
             reg_offset=1,
             reg_wordswap=True,
             file_type="csv",
             file_path="./SungrowSHxxRT.csv")

i = 10
# application loop
while mb.process_batches(close_socket=True):
    print(mb.results)
    i -= 1
    if not i:
        break
    time.sleep(10)
exit( 1 )
