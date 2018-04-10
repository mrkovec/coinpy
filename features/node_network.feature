Feature: Nodes forming network

  Scenario: Node connects to another node
    Given we have running node "A"
      And we have running node "B"
    When node "A" sends "greet" message to node "B"
    Then node "B" receives "greet" message from node "A"
      And node "B" sends "info" message to node "A"
    Then node "A" receives "info" message from node "B"
      And node "A" stops
      And node "B" stops

  Scenario: Node connects to his neighbors
    Given we have running node "A"
      And we have running node "B"
      And we have running node "C"
      And node "B" is neighbor of node "A"
      And node "C" is neighbor of node "A"
    When node "A" sends "greet" message to his neighbors
    Then node "B" receives "greet" message from node "A"
      And node "B" sends "info" message to node "A"
    Then node "C" receives "greet" message from node "A"
      And node "C" sends "info" message to node "A"
    Then node "A" receives "info" message from node "B"
    Then node "A" receives "info" message from node "C"
      And node "A" stops
      And node "B" stops
      And node "C" stops
