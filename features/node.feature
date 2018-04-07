Feature: Nodes mining blocks

  Scenario: Mine new block
    Given we have running node "A" on port "5010"
      When node "A" mines new block
        And node "A" validates new block
      Then node "A" adds new block to his blockchain

  Scenario: Mine and announce new block
    Given we have running node "A" on port "5011"
      And we have running node "B" on port "5012"
      When node "A" mines new block
        And node "A" validates new block
        And node "A" adds new block to his blockchain
      Then node "A" announces new block to node "B"
      Then node "B" receives new block
        And node "B" validates new block
        And node "B" adds new block to his blockchain
