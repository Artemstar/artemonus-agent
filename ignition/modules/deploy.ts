import { createPublicClient, createWalletClient, http } from "viem";
import { privateKeyToAccount } from "viem/accounts";
import { sepolia } from "viem/chains";
import * as dotenv from "dotenv";
import { readFileSync } from "fs";
import { join } from "path";

dotenv.config();

async function main() {
  const rawKey = process.env.PRIVATE_KEY!;
  const privateKey = rawKey.startsWith("0x") ? rawKey as `0x${string}` : `0x${rawKey}` as `0x${string}`;
  const account = privateKeyToAccount(privateKey);

  const rpcUrl = `https://eth-sepolia.g.alchemy.com/v2/${process.env.ALCHEMY_API_KEY}`;

  const publicClient = createPublicClient({
    chain: sepolia,
    transport: http(rpcUrl),
  });

  const walletClient = createWalletClient({
    account,
    chain: sepolia,
    transport: http(rpcUrl),
  });

  console.log("Deploying ArtemAgent to Sepolia...");
  console.log("Deployer:", account.address);

  const balance = await publicClient.getBalance({ address: account.address });
  console.log("Balance:", balance.toString(), "wei");

  if (balance === 0n) {
    throw new Error("No Sepolia ETH! Get some at https://sepoliafaucet.com");
  }

  const artifact = JSON.parse(
    readFileSync(join(process.cwd(), "artifacts/contracts/ArtemAgent.sol/ArtemAgent.json"), "utf-8")
  );

  const hash = await walletClient.deployContract({
    abi: artifact.abi,
    bytecode: artifact.bytecode as `0x${string}`,
    args: [
      "ArtemAgent",
      "artemonus.eth",
      "AI agent identity contract for artemonus.eth — autonomous, on-chain, open source.",
    ],
  });

  console.log("Transaction hash:", hash);
  console.log("Waiting for confirmation...");

  const receipt = await publicClient.waitForTransactionReceipt({ hash });
  console.log("✅ ArtemAgent deployed to:", receipt.contractAddress);
  console.log("🔗 Etherscan:", `https://sepolia.etherscan.io/address/${receipt.contractAddress}`);
}

main().catch((e) => {
  console.error(e);
  process.exit(1);
});
