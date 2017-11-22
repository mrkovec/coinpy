[![Build Status](https://travis-ci.org/mrkovec/coinpy.svg?branch=master)](https://travis-ci.org/mrkovec/coinpy)
[![Coverage Status](https://coveralls.io/repos/github/mrkovec/coinpy/badge.svg)](https://coveralls.io/github/mrkovec/coinpy)
# coinpy
```
+---------------+    +----------------------------+      +-----------------------------+              
|    output     |    |        transaction         |      |            block            |              
+---------------+    +----------------------------+      +-----------------------------+              
|    amount     |    |           version          |      |          version            |              
|    pubaddr    |    |          time_stamp        |      |           nonce             |              
+-------|-------+    | +------------+-----------+ |      |       prev_block_id         |              
        |            | |  inputs    | outputs   | |      |           height            |              
        |            | +------------+-----------+ |      |         difficulty          |              
+-------v-------+    | |output1.id  | output1   | |      |         time_stamp          |              
|   output.id   |    | |output2.id  ------------- |      |  +-----------------------+  |              
+---------------+    | |            |           | |      |  |     transactions      |  |              
                     | |            |           | |      |  +-----------------------+  |              
                     | |            ------------- |      |  |    transaction1.id    |  |              
                     | |outputN.id  | outputN   | |      |  |    transaction2.id    |  |              
                     | +------------+-----------+ |      |  |                       |  |              
                     +----------------------------+      |  |                       |  |              
                     |              |             |      |  |    transactionN.id    |  |              
                     |              |             |      |  +-----------------------+  |              
                     |     +--------v-------+     |      +--------------|--------------+              
                     |     |   signature    |     |                     |                             
                     |     +----------------+     |                     |                             
                     |      signature_pubkey      |      +--------------v--------------+              
                     +----------------------------+      |           block.id          |              
                                    |                    +-----------------------------+              
                                    |                                                                 
                     +----------------------------+                                                   
                     |       transaction.id       |                                                   
                     +----------------------------+                                                   
                                                                                                      
```