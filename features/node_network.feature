Feature: Nodes forming network

  Scenario: Node connects to his neighbor
    Given we have running node "A"
      And we have running node "B"
      And node "B" is neighbor of node "A"
    Then node "A" sends "greet" message to node "B"
    Then node "B" receives "greet" message from node "A"
      And node "B" sends "info" message to node "A"
    Then node "A" receives "info" message from node "B"
