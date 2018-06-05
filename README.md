# Blockchain Sample Code

## Refer to:

[Learn Blockchains by Building One](https://hackernoon.com/learn-blockchains-by-building-one-117428612f46)

[用Python从零开始创建区块链](https://learnblockchain.cn/2017/10/27/build_blockchain_by_python/)

## API features

**1. Return information of all block on the chain**

    Methods: GET
    URL: http://127.0.0.1:5000/chain
    Header : Content-Type: application/json

**2. Add a new transaction on the node**

    Methods: POST
    URL: http://127.0.0.1:5000/transactions/new
    Header : Content-Type: application/json
    Body:
    {
        "sender": "d4ee26eee15148ee92c6cd394edd974e",
        "recipient": "someone-other-address",
        "amount": 5
    }

**3. Mine the block on the node**

    Methods: GET
    URL: http://127.0.0.1:5000/mine
    Header : Content-Type: application/json

**4. Register neighbours nodes**

    Methods: POST
    URL: http://127.0.0.1:5000/nodes/register
    Header : Content-Type: application/json
    Body:
    {
        "nodes": ["http://127.0.0.1:5001"]
    }

**5. resolve conflicts of chain**

    Methods: GET
    URL: http://127.0.0.1:5000/nodes/resolve
    Header : Content-Type: application/json