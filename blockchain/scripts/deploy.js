const { ethers } = require("hardhat");

async function main() {
  console.log("Deploying TruthLensRegistry contract...");

  const TruthLensRegistry = await ethers.getContractFactory("TruthLensRegistry");
  const truthLensRegistry = await TruthLensRegistry.deploy();

  await truthLensRegistry.deployed();

  console.log("TruthLensRegistry deployed to:", truthLensRegistry.address);
  console.log("Transaction hash:", truthLensRegistry.deployTransaction.hash);
  
  // Verify contract on Polygonscan (optional)
  console.log("\nTo verify on Polygonscan, run:");
  console.log(`npx hardhat verify --network mumbai ${truthLensRegistry.address}`);
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });