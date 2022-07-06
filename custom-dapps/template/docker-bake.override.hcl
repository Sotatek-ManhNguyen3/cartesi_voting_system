
target "dapp" {
}

target "server" {
  tags = ["cartesi/dapp:voting-devel-server"]
}

target "console" {
  tags = ["cartesi/dapp:voting-devel-console"]
}

target "machine" {
  tags = ["cartesi/dapp:voting-devel-machine"]
}
