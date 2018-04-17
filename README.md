[![Build Status](https://travis-ci.org/mrkovec/coinpy.svg?branch=master)](https://travis-ci.org/mrkovec/coinpy)
[![Coverage Status](https://coveralls.io/repos/github/mrkovec/coinpy/badge.svg)](https://coveralls.io/github/mrkovec/coinpy)
# coinpy
Python implementation of a basic blockchain (bitcoin inspired and simplified) functionality for learning purposes (python3/asyncio/xmlrpc).

For now, the best way to inspect working functionality is thru browsing unit and [behave](https://github.com/behave/behave) tests.

```bash
git clone https://github.com/mrkovec/coinpy.git
python -m pip install mypy
python -m pip install mypy_extensions
python -m pip install ecdsa
python -m pip install behave

python -m unittest discover
python -m behave
```
Also is possible to inspect nodes communication with:

runing first node
```bash
python -m coinpyd -bind localhost:5001 -rpcbind localhost:6001 
```
runing second node
```bash
python -m coinpyd -bind localhost:5002 -addnode  localhost:5001 -gen -rpcbind localhost:6002
```
inspecting log outputs and afterwards quitting nodes 
```bash
python -m coinpycli stop 127.0.0.1:6001
python -m coinpycli stop 127.0.0.1:6002
```

Functionality overview:

- [x] output/transaction/block/ledger data and functionality design
```
+---------------+    +----------------------------+      +-----------------------------+              
|    output     |    |        transaction         |      |            block            |              
+---------------+    +----------------------------+      +-----------------------------+              
|    amount     |    |           version          |      |          version            |              
|    pubaddr    |    |          time_stamp        |      |           nonce             |              
+-------+-------+    | +------------+-----------+ |      |       prev_block_id         |              
        |            | |  inputs    | outputs   | |      |           height            |              
+-------v-------+    | +------------+-----------+ |      |         difficulty          |              
|   output.id   |    | |output1.id  | output1   | |      |         time_stamp          |              
+---------------+    | |output2.id  +-----------+ |      |  +-----------------------+  |              
                     | |     .      |     .     | |      |  |     transactions      |  |              
                     | |     .      |     .     | |      |  +-----------------------+  |              
                     | |     .      +-----------+ |      |  |     transaction1      |  |              
                     | |outputN.id  | outputN   | |      |  |     transaction2      |  |              
                     | +------------+-----------+ |      |  |          .            |  |              
                     +--------------+-------------+      |  |          .            |  |              
                     |              |             |      |  |     transactionN      |  |              
                     |     +--------v-------+     |      |  +-----------------------+  |              
                     |     |   signature    |     |      +--------------+--------------+              
                     |     +----------------+     |                     |                             
                     |      signature_pubkey      |      +--------------v--------------+              
                     +--------------+-------------+      |           block.id          |              
                                    |                    +-----------------------------+              
                     +--------------v-------------+                   
                     |       transaction.id       |                                                   
                     +----------------------------+                                                   
```
```
+--------------------------------------------------------------------------------------------------------------------------------+   
|                                                            blockchain                                                          |   
+--------------------------------------------------------------------------------------------------------------------------------+   
|      +--------------------------------------------+                           +------------------------------------------+     |   
|      |                    blockN                  +-------------+             |                  blockN+1                +---->+     
|      +--------------------------------------------+             |             +------------------------------------------+     |   
+----->+                prev_block_id               |             +------------>+                prev_block_id             |     |   
|      +--------------------------------------------+                           +------------------------------------------+     |   
|      |                 transactionN               |                           |              transactionN                |     |   
| +--->+ inputM from pubadrA     outputM to pubadrC +-+                    ---->+ inputM from pubadrB   outputM to pubadrD +--+  |   
| |    | inputM+1 from pubadrA                      | |                    |    +------------------------------------------+  |  |   
| |    |--------------------------------------------| |                    |    |                transactionN+1            |  |  |   
| |    |               transactionN+1               | |                    | -->+ inputM from oubadrC   outputM to pubadrD +--+  |   
| | +->+ inputM from pubadrB   outputM to pubadrC   +-+                    | |  |                                          |  |  |   
| | |  +--------------------------------------------+ |                    | |  +------------------------------------------+  |  |   
+-|-|-------------------------------------------------|--------------------|-|------------------------------------------------|--+   
  | |                                                 |  +---------------+ | |                                                |      
  | |                                                 |  |unspent outputs| | |                                                |      
  | |                                                 |  +---------------+ | |                                                |      
  +-|-------------------------------------------------|------ pubadrA    | | |                                                |      
    |                                                 |  |               | | |                                                |      
    +-------------------------------------------------|------ pubadrB -----+ |                                                |      
                                                      |  |               |   |                                                |      
                                                      +-----> pubadrC -------+                                                |      
                                                         |               |                                                    |      
                                                         |    pubadrD <-------------------------------------------------------+     
                                                         |               |                                                           
                                                         +---------------+                                                           
```
- [x] peer-to-peer functionality
- [x] consensus rules
- [x] block assembling, mining, announcing and chaining
- [x] between nodes blockchain sync 
- [x] basic daemon / cli functionality
- [ ] fork merging
- [ ] blockchain persistence
- [ ] wallet functionality
- [ ] NAT traversal
- [ ] IPFS
