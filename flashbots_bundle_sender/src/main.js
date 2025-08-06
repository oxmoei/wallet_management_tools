const path = require("path");
require("dotenv").config({ path: path.join(__dirname, "..", ".env") });

const { ethers } = require("ethers");
const { FlashbotsBundleProvider } = require("@flashbots/ethers-provider-bundle");
const fs = require("fs");
const readline = require("readline");

// 颜色代码定义
const colors = {
  reset: "\x1b[0m",
  bright: "\x1b[1m",
  dim: "\x1b[2m",
  red: "\x1b[31m",
  green: "\x1b[32m",
  yellow: "\x1b[33m",
  blue: "\x1b[34m",
  magenta: "\x1b[35m",
  cyan: "\x1b[36m",
  white: "\x1b[37m",
  bgRed: "\x1b[41m",
  bgGreen: "\x1b[42m",
  bgYellow: "\x1b[43m",
  bgBlue: "\x1b[44m",
  bgMagenta: "\x1b[45m",
  bgCyan: "\x1b[46m"
};

// 程序横幅
const banner = `
${colors.bgMagenta}${colors.white}${"═".repeat(80)}${colors.reset}
${colors.bgMagenta}${colors.white}  ╔══════════════════════════════════════════════════════════════════════════╗  ${colors.reset}
${colors.bgMagenta}${colors.white}  ║                                                                          ║  ${colors.reset}
${colors.bgMagenta}${colors.white}  ║             ${colors.bright}${colors.yellow}🚀 FLASHBOTS BUNDLE TRANSACTION SENDER 🚀${colors.reset}${colors.bgMagenta}${colors.white}                    ║  ${colors.reset}
${colors.bgMagenta}${colors.white}  ║                                                                          ║  ${colors.reset}
${colors.bgMagenta}${colors.white}  ║          ${colors.cyan}MEV Bundle Transaction Tool for Ethereum Networks${colors.reset}${colors.bgMagenta}${colors.white}               ║  ${colors.reset}
${colors.bgMagenta}${colors.white}  ║                      ${colors.cyan}FlashBots 交易捆绑发送器${colors.reset}${colors.bgMagenta}${colors.white}                            ║  ${colors.reset}
${colors.bgMagenta}${colors.white}  ║                                                                          ║  ${colors.reset}
${colors.bgMagenta}${colors.white}  ║            ${colors.green}Version: 1.2.0${colors.reset}${colors.bgMagenta}${colors.white}           ${colors.bgMagenta}${colors.white}    ${colors.cyan}Network: Sepolia${colors.reset}${colors.bgMagenta}${colors.white}                 ║  ${colors.reset}
${colors.bgMagenta}${colors.white}  ║                                                                          ║  ${colors.reset}
${colors.bgMagenta}${colors.white}  ╚══════════════════════════════════════════════════════════════════════════╝  ${colors.reset}
${colors.bgMagenta}${colors.white}${"═".repeat(80)}${colors.reset}
`;

// 美化输出函数
const log = {
  info: (msg) => console.log(`${colors.cyan}ℹ️  ${msg}${colors.reset}`),
  success: (msg) => console.log(`${colors.green}✅  ${msg}${colors.reset}`),
  warning: (msg) => console.log(`${colors.yellow}⚠️  ${msg}${colors.reset}`),
  error: (msg) => console.log(`${colors.red}❌ ${msg}${colors.reset}`),
  title: (msg) => console.log(`${colors.bright}${colors.blue}🎯  ${msg}${colors.reset}`),
  section: (msg) => console.log(`${colors.magenta}📋  ${msg}${colors.reset}`),
  data: (msg) => console.log(`${colors.dim}${msg}${colors.reset}`),
  highlight: (msg) => console.log(`${colors.bright}${colors.green}${msg}${colors.reset}`),
  separator: () => console.log(`${colors.blue}${"─".repeat(60)}${colors.reset}`),
  header: (msg) => console.log(`\n${colors.bgBlue}${colors.white} ${msg} ${colors.reset}\n`),
  banner: () => console.log(banner)
};

// 从 .env 文件加载必要的环境变量
const {
  ETHEREUM_RPC_URL,
  FLASHBOTS_RELAY_URL,
  SAFE_WALLET_PRIVATE_KEY,
  TAR_WALLET_PRIVATE_KEY,
  FLASHBOTS_RELAY_SIGNING_KEY,
  SAFE_TO_TAR_AMOUNT,
  CONTRACT_ADDRESS,
  HEX_DATA,
  GAS_LIMIT,
  MAX_PRIORITY_FEE,
} = process.env;

// 创建以太坊 RPC 提供者
async function createProvider() {
  const provider = new ethers.JsonRpcProvider(ETHEREUM_RPC_URL);
  const network = await provider.getNetwork();
  log.header("🔗 以太坊网络连接");
  log.info(`RPC提供者: ${ETHEREUM_RPC_URL}`);
  log.success(`Chain_ID: ${network.chainId}`);
  log.separator();
  return { provider, chainId: network.chainId };
}

const RETRY_DELAY = 2000; // 重试间隔（毫秒）
const MAX_RETRIES = 15;  // 增加最大重试次数

// 延迟函数
async function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

// 用户确认函数
async function askForConfirmation(message) {
  const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout
  });

  return new Promise((resolve) => {
    rl.question(`${colors.bright}${colors.yellow}${message} (y/N): ${colors.reset}`, (answer) => {
      rl.close();
      const confirmed = answer.toLowerCase() === 'y' || answer.toLowerCase() === 'yes';
      if (confirmed) {
        log.success("用户确认发送交易捆绑");
      } else {
        log.warning("用户取消发送交易捆绑");
      }
      resolve(confirmed);
    });
  });
}

// 检查网络状态
async function checkNetworkStatus(provider) {
  try {
    const feeData = await provider.getFeeData();
    const blockNumber = await provider.getBlockNumber();
    const block = await provider.getBlock(blockNumber);
    
    log.section("🌐 网络状态检查");
    log.info(`当前区块: ${blockNumber}`);
    log.info(`区块Gas限制: ${block.gasLimit.toString()}`);
    log.info(`区块Gas使用: ${block.gasUsed.toString()}`);
    log.info(`Gas使用率: ${((Number(block.gasUsed) / Number(block.gasLimit)) * 100).toFixed(2)}%`);
    log.info(`基础费用: ${ethers.formatUnits(feeData.lastBaseFeePerGas || 0, "gwei")} gwei`);
    log.info(`建议优先费用: ${ethers.formatUnits(feeData.maxPriorityFeePerGas || 0, "gwei")} gwei`);
    
    // 计算建议的Gas费用
    const baseFee = feeData.lastBaseFeePerGas || 0;
    const suggestedPriorityFee = feeData.maxPriorityFeePerGas || ethers.parseUnits("1", "gwei");
    const suggestedMaxFee = baseFee + suggestedPriorityFee + ethers.parseUnits("10", "gwei"); // 额外缓冲
    
    log.info(`建议最大费用: ${ethers.formatUnits(suggestedMaxFee, "gwei")} gwei`);
    log.info(`建议优先费用: ${ethers.formatUnits(suggestedPriorityFee, "gwei")} gwei`);
    
    // 检查网络拥堵情况
    const gasUsage = Number(block.gasUsed) / Number(block.gasLimit);
    if (gasUsage > 0.8) {
      log.warning("⚠️  网络拥堵！Gas使用率超过80%，建议提高Gas费用");
    } else if (gasUsage > 0.6) {
      log.warning("⚠️  网络较忙，Gas使用率超过60%");
    } else {
      log.success("✅ 网络状态良好");
    }
    
    log.separator();
    
    return {
      gasUsage: gasUsage,
      baseFee: baseFee,
      priorityFee: suggestedPriorityFee,
      suggestedMaxFee: suggestedMaxFee
    };
  } catch (error) {
    log.warning("无法获取网络状态信息");
    return null;
  }
}

// 发送交易捆绑，并支持重试，直到成功上链
async function sendBundle(provider, flashbotsProvider, bundleTransactions) {
  let attempt = 1;  // 初始化尝试次数

  while (true) {  // 无限循环，直到成功上链或达到最大重试次数
    const blockNumber = await provider.getBlockNumber();
    const targetBlockNumber = blockNumber + 1;
    log.header(`🚀 第 ${attempt} 次尝试发送交易捆绑`);
    log.info(`目标区块: ${targetBlockNumber}`);
    
    // 动态调整Gas费用（每次失败都提高）
    if (attempt > 1) {
      const increaseFactor = attempt; // 每次失败都提高
      const newMaxFeePerGas = bundleTransactions[0].transaction.maxFeePerGas * BigInt(2); // 每次翻倍
      const newMaxPriorityFeePerGas = bundleTransactions[0].transaction.maxPriorityFeePerGas * BigInt(2); // 每次翻倍
      
      log.warning(`第${attempt}次尝试，提高Gas费用（翻倍）`);
      log.info(`新的maxFeePerGas: ${ethers.formatUnits(newMaxFeePerGas, "gwei")} gwei`);
      log.info(`新的maxPriorityFeePerGas: ${ethers.formatUnits(newMaxPriorityFeePerGas, "gwei")} gwei`);
      
      // 更新所有交易的Gas费用
      bundleTransactions.forEach(tx => {
        tx.transaction.maxFeePerGas = newMaxFeePerGas;
        tx.transaction.maxPriorityFeePerGas = newMaxPriorityFeePerGas;
      });
    }
    
    log.separator();

    // 辅助函数：将 BigNumbers 转换为字符串
    const bigNumberToString = (key, value) =>
      typeof value === "bigint" ? value.toString() : value;

    log.section("交易捆绑详情:");
    log.data(JSON.stringify(bundleTransactions, bigNumberToString, 2));
    log.separator();

    // 签署交易捆绑
    const signedBundle = await flashbotsProvider.signBundle(bundleTransactions);

    // 进行模拟执行，检查交易是否有效
    const simulation = await flashbotsProvider.simulate(signedBundle, targetBlockNumber);
    if ("error" in simulation) {
      log.error("模拟执行失败:");
      log.data(JSON.stringify(simulation.error, null, 2));
    } else {
      log.success("模拟执行成功:");
      log.data(JSON.stringify(simulation, bigNumberToString, 2));
    }

    log.separator();

    // 询问用户是否发送交易捆绑（仅在第一次尝试时确认）
    let confirmed = true;
    if (attempt === 1) {
      confirmed = await askForConfirmation("是否发送此交易捆绑？");
      if (!confirmed) {
        log.warning("用户取消发送，跳过此次尝试");
        attempt++; // 增加尝试次数
        if (attempt > MAX_RETRIES) {
          log.error("超过最大重试次数，停止重试");
          break; // 超过最大重试次数，退出循环
        }
        await sleep(RETRY_DELAY);
        continue; // 继续重试
      }
    }

    // 发送交易捆绑
    const bundleResponse = await flashbotsProvider.sendBundle(bundleTransactions, targetBlockNumber);

    if ("error" in bundleResponse) {
      log.error("发送交易捆绑失败:");
      log.data(JSON.stringify(bundleResponse.error, null, 2));
      
      // 检查是否是Gas费用相关错误
      const errorMessage = JSON.stringify(bundleResponse.error).toLowerCase();
      if (errorMessage.includes("gas") || errorMessage.includes("fee")) {
        log.warning("可能是Gas费用问题，建议提高Gas费用");
      }
      
      await sleep(RETRY_DELAY);
      attempt++; // 增加尝试次数
      if (attempt > MAX_RETRIES) {
        log.error("超过最大重试次数，停止重试");
        break; // 超过最大重试次数，退出循环
      }
      continue; // 继续重试
    }

    log.success("交易捆绑发送成功:");
    log.data(JSON.stringify(bundleResponse, bigNumberToString, 2));
    log.separator();

    // 等待交易结果
    try {
      const bundleReceipt = await bundleResponse.wait();
      if (bundleReceipt.status === 1) {
        log.highlight(`🎉 交易成功包含在区块 ${bundleReceipt.blockNumber} 中`);
        log.success(`Transaction Hash: ${bundleReceipt.transactionHash}`);
        break; // 成功上链后跳出循环
      } else {
        log.warning("交易捆绑未能成功上链");
        log.data(`Bundle Hash: ${bundleResponse.bundleHash}`);
        attempt++; // 增加尝试次数
        if (attempt > MAX_RETRIES) {
          log.error("超过最大重试次数，停止重试");
          break; // 超过最大重试次数，退出循环
        }
        await sleep(RETRY_DELAY); // 重试前的延迟
      }
    } catch (error) {
      log.error("等待交易结果时出错:");
      log.data(error.message);
      log.warning("交易可能未被包含在区块中");
      
      // 检查目标区块是否已经被挖出
      try {
        const currentBlock = await provider.getBlockNumber();
        if (currentBlock >= targetBlockNumber) {
          log.warning(`目标区块 ${targetBlockNumber} 已被挖出，但交易未被包含`);
          log.info("可能原因：Gas费用不够高或网络拥堵");
        }
      } catch (blockError) {
        log.warning("无法检查区块状态");
      }
      
      attempt++; // 增加尝试次数
      if (attempt > MAX_RETRIES) {
        log.error("超过最大重试次数，停止重试");
        break; // 超过最大重试次数，退出循环
      }
      await sleep(RETRY_DELAY); // 重试前的延迟
    }

    log.separator();

    // 获取交易捆绑的统计数据
    try {
      const bundleStats = await flashbotsProvider.getBundleStatsV2(bundleResponse.bundleHash, targetBlockNumber);
      log.section("交易捆绑统计:");
      log.data(JSON.stringify(bundleStats, bigNumberToString, 2));
      
      // 分析失败原因
      if (bundleStats && bundleStats.isSimulated && !bundleStats.isIncluded) {
        log.warning("交易模拟成功但未被包含，可能的原因：");
        log.info("1. Gas费用不够高");
        log.info("2. 网络拥堵");
        log.info("3. 矿工偏好问题");
        log.info("4. 交易顺序问题");
        
        // 建议提高Gas费用
        const currentMaxFee = bundleTransactions[0].transaction.maxFeePerGas;
        const currentPriorityFee = bundleTransactions[0].transaction.maxPriorityFeePerGas;
        const suggestedMaxFee = currentMaxFee * BigInt(2);
        const suggestedPriorityFee = currentPriorityFee * BigInt(2);
        
        log.warning("建议提高Gas费用：");
        log.info(`当前maxFeePerGas: ${ethers.formatUnits(currentMaxFee, "gwei")} gwei`);
        log.info(`建议maxFeePerGas: ${ethers.formatUnits(suggestedMaxFee, "gwei")} gwei`);
        log.info(`当前maxPriorityFeePerGas: ${ethers.formatUnits(currentPriorityFee, "gwei")} gwei`);
        log.info(`建议maxPriorityFeePerGas: ${ethers.formatUnits(suggestedPriorityFee, "gwei")} gwei`);
        
        // 自动更新Gas费用
        bundleTransactions.forEach(tx => {
          tx.transaction.maxFeePerGas = suggestedMaxFee;
          tx.transaction.maxPriorityFeePerGas = suggestedPriorityFee;
        });
      }
    } catch (error) {
      log.warning("无法获取交易捆绑统计信息");
      log.data(error.message);
    }
  }
  log.highlight("🎉 交易上链成功或重试已达到最大次数，退出循环。");
}

// 循环发送交易
async function loopSend() {
  const { provider, chainId } = await createProvider();
  const safeWallet = new ethers.Wallet(SAFE_WALLET_PRIVATE_KEY, provider);
  const tarWallet = new ethers.Wallet(TAR_WALLET_PRIVATE_KEY, provider);
  const tarWallet_address = await tarWallet.getAddress();
  
  // 连接 Flashbots 提供者
  const flashbotsProvider = await FlashbotsBundleProvider.create(
    provider,
    new ethers.Wallet(FLASHBOTS_RELAY_SIGNING_KEY),
    FLASHBOTS_RELAY_URL
  );

  // 设定 Gas 费用 - 提高费用以增加被接受的概率
  const maxPriorityFee = MAX_PRIORITY_FEE || "100"; // 提高默认优先费用到100 gwei
  const maxFeePerGas = ethers.parseUnits("500", "gwei");  // 提高最大费用到500 gwei
  const maxPriorityFeePerGas = ethers.parseUnits(maxPriorityFee, "gwei");
  
  // 确保 maxPriorityFeePerGas 不大于 maxFeePerGas
  let gasSettings;
  if (maxPriorityFeePerGas > maxFeePerGas) {
    log.warning(`maxPriorityFeePerGas (${maxPriorityFee} gwei) 大于 maxFeePerGas (100 gwei)，已自动调整`);
    const adjustedMaxFeePerGas = maxPriorityFeePerGas + ethers.parseUnits("1", "gwei");
    log.info(`调整后的 maxFeePerGas: ${ethers.formatUnits(adjustedMaxFeePerGas, "gwei")} gwei`);
    
    gasSettings = {
      maxFeePerGas: adjustedMaxFeePerGas,
      maxPriorityFeePerGas: maxPriorityFeePerGas,
    };
  } else {
    gasSettings = {
      maxFeePerGas: maxFeePerGas,
      maxPriorityFeePerGas: maxPriorityFeePerGas,
    };
  }

  // 验证必要的环境变量
  if (!CONTRACT_ADDRESS) {
    throw new Error("缺少 CONTRACT_ADDRESS 环境变量");
  }
  if (!HEX_DATA) {
    throw new Error("缺少 HEX_DATA 环境变量");
  }
  if (!GAS_LIMIT) {
    throw new Error("缺少 GAS_LIMIT 环境变量");
  }
  if (!SAFE_TO_TAR_AMOUNT) {
    throw new Error("缺少 SAFE_TO_TAR_AMOUNT 环境变量");
  }
  if (!SAFE_WALLET_PRIVATE_KEY) {
    throw new Error("缺少 SAFE_WALLET_PRIVATE_KEY 环境变量");
  }
  if (!TAR_WALLET_PRIVATE_KEY) {
    throw new Error("缺少 TAR_WALLET_PRIVATE_KEY 环境变量");
  }
  if (!FLASHBOTS_RELAY_SIGNING_KEY) {
    throw new Error("缺少 FLASHBOTS_RELAY_SIGNING_KEY 环境变量");
  }

  // 检查钱包余额
  const safeWalletBalance = await provider.getBalance(safeWallet.address);
  const tarWalletBalance = await provider.getBalance(tarWallet_address);
  const requiredAmount = ethers.parseUnits(SAFE_TO_TAR_AMOUNT, "ether");
  
  log.header("📋 交易配置");
  log.info(`合约地址: ${CONTRACT_ADDRESS}`);
  log.info(`十六进制数据: ${HEX_DATA}`);
  log.info(`Gas限制: ${GAS_LIMIT}`);
  log.info(`转账金额: ${SAFE_TO_TAR_AMOUNT} ETH`);
  log.info(`最大优先费用: ${maxPriorityFee} gwei`);
  log.info(`Safe钱包余额: ${ethers.formatEther(safeWalletBalance)} ETH`);
  log.info(`目标钱包余额: ${ethers.formatEther(tarWalletBalance)} ETH`);
  
  // 检查余额是否足够
  if (safeWalletBalance < requiredAmount) {
    throw new Error(`Safe钱包余额不足！需要 ${SAFE_TO_TAR_AMOUNT} ETH，当前余额 ${ethers.formatEther(safeWalletBalance)} ETH`);
  }
  
  // 估算Gas费用
  const estimatedGasCost = gasSettings.maxFeePerGas * BigInt(GAS_LIMIT);
  log.info(`预估Gas费用: ${ethers.formatEther(estimatedGasCost)} ETH`);
  
  if (tarWalletBalance < estimatedGasCost) {
    log.warning(`目标钱包余额可能不足以支付Gas费用！`);
  }
  
  log.separator();

  // 组装交易捆绑
  const bundleTransactions = [
    {
      signer: safeWallet,
      transaction: {
        to: tarWallet_address,
        value: ethers.parseUnits(SAFE_TO_TAR_AMOUNT, "ether"),
        chainId,
        gasLimit: 21000,
        maxFeePerGas: gasSettings.maxFeePerGas,
        maxPriorityFeePerGas: gasSettings.maxPriorityFeePerGas,
        type: 2,
      },
    },
    {
      signer: tarWallet,
      transaction: {
        to: CONTRACT_ADDRESS,
        data: HEX_DATA,
        value: 0,
        chainId,
        gasLimit: parseInt(GAS_LIMIT),
        maxFeePerGas: gasSettings.maxFeePerGas,
        maxPriorityFeePerGas: gasSettings.maxPriorityFeePerGas,
        type: 2,
      },
    },
  ];

  // 询问用户是否开始发送交易
  log.header("🚀 准备开始发送交易捆绑");
  const startConfirmed = await askForConfirmation("是否开始发送交易捆绑？");
  if (!startConfirmed) {
    log.warning("用户取消操作，程序退出");
    process.exit(0);
  }

  log.info("确认模式: 仅首次确认，后续自动重试");

  // 无限循环发送交易
  while (true) {
    // 检查网络状态
    const networkStatus = await checkNetworkStatus(provider);
    
    // 根据网络状态调整Gas费用
    if (networkStatus) {
      if (networkStatus.gasUsage > 0.7) {
        log.warning("检测到网络拥堵，自动提高Gas费用");
        const adjustedMaxFeePerGas = networkStatus.suggestedMaxFee * BigInt(3); // 3倍
        const adjustedMaxPriorityFeePerGas = networkStatus.priorityFee * BigInt(5); // 5倍
        
        bundleTransactions.forEach(tx => {
          tx.transaction.maxFeePerGas = adjustedMaxFeePerGas;
          tx.transaction.maxPriorityFeePerGas = adjustedMaxPriorityFeePerGas;
        });
        
        log.info(`调整后的maxFeePerGas: ${ethers.formatUnits(adjustedMaxFeePerGas, "gwei")} gwei`);
        log.info(`调整后的maxPriorityFeePerGas: ${ethers.formatUnits(adjustedMaxPriorityFeePerGas, "gwei")} gwei`);
      } else if (networkStatus.gasUsage > 0.5) {
        log.warning("检测到网络较忙，适度提高Gas费用");
        const adjustedMaxFeePerGas = networkStatus.suggestedMaxFee * BigInt(2); // 2倍
        const adjustedMaxPriorityFeePerGas = networkStatus.priorityFee * BigInt(3); // 3倍
        
        bundleTransactions.forEach(tx => {
          tx.transaction.maxFeePerGas = adjustedMaxFeePerGas;
          tx.transaction.maxPriorityFeePerGas = adjustedMaxPriorityFeePerGas;
        });
        
        log.info(`调整后的maxFeePerGas: ${ethers.formatUnits(adjustedMaxFeePerGas, "gwei")} gwei`);
        log.info(`调整后的maxPriorityFeePerGas: ${ethers.formatUnits(adjustedMaxPriorityFeePerGas, "gwei")} gwei`);
      }
    }
    
    await sendBundle(provider, flashbotsProvider, bundleTransactions);
    // 等待一段时间后再次发送交易
    await sleep(60000); // 1分钟后再发送
  }
}

// 显示程序横幅
log.banner();

// 添加紧急停止处理
process.on('SIGINT', () => {
  log.warning("\n⚠️  检测到 Ctrl+C，正在安全停止程序...");
  log.info("正在清理资源...");
  setTimeout(() => {
    log.success("程序已安全停止");
    process.exit(0);
  }, 1000);
});

// 运行循环发送交易函数
loopSend().catch((error) => {
  log.error("程序执行出错:");
  log.data(error.message);
  process.exit(1);
});
