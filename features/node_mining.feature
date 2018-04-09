Feature: Nodes mining blocks

  Scenario: Mine new block
    Given we have running node "A"
      When node "A" mines new block
        And node "A" validates new block
      Then node "A" adds new block to his blockchain
        And node "A" stops

  Scenario: Mine and announce new block
    Given we have running node "A"
      And we have running node "B"
      When node "A" mines new block
        And node "A" validates new block
        And node "A" adds new block to his blockchain
      Then node "A" sends "newblock" message to node "B"
      Then node "B" receives "newblock" message from node "A"
        And node "B" validates new block
        And node "B" adds new block to his blockchain
      Then node "A" stops
        And node "B" stops

  Scenario: Mine new block with external miner
    Given we have running node "A"
      And node "A" listens for external mined block
    When we have running "coinpy-cpp-miner"
      And external miner sends new block to node "A"
    Then node "A" validates new block
      And node "A" stops
