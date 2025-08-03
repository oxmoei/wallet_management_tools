const crypto = require('crypto'); 
globalThis.crypto = crypto;
const https = require('https');
const querystring = require('querystring');
const chalk = require('chalk'); // 用于美化输出
const readline = require('readline'); // 重新添加readline模块用于控制台输入
const path = require('path'); // 添加path模块支持多平台路径
require('dotenv').config({ path: path.join(__dirname, '../.env') });

// 从 .env 文件中加载 API 配置信息
const api_config = {
  api_key: process.env.OKX_API_KEY,
  secret_key: process.env.OKX_SECRET_KEY,
  passphrase: process.env.OKX_PASSPHRASE,
  project: process.env.OKX_PROJECT
};

// 从chains.json 文件中加载链列表
const chainsPath = path.join(__dirname, '../chains.json');
let chains;
try {
  chains = JSON.parse(require('fs').readFileSync(chainsPath, 'utf-8'));
} catch (error) {
  console.error(chalk.red.bold(`❌  无法加载链列表: ${error.message}`));
  process.exit(1);
}

// 延迟时间和批量查询设置
const delayBetweenRequests = 1500; // 设置请求间隔为 1.5 秒
const batchSize = 1; // 每次查询 1 个地址

// 程序横幅
console.log(chalk.magentaBright.bold.inverse('基于OKX_OS钱包API'));
console.log(chalk.cyan.bold(`
     ____  _   _  _____   ____  _  __ _____  ____
    / ___|| | | || ____| / ___|| |/ /| ____||  _ \\
   | |    | |_| ||  _|  | |    | ' / |  _|  | |_) |
   | |___ |  _  || |___ | |___ | . \\ | |___ |  _ <
    \\____||_| |_||_____| \\____||_|\\_\\|_____||_| \\_\\
`));
console.log(
  chalk.yellowBright.bold.inverse('💥 批量钱包资产余额查询工具') + '       ' +
  chalk.yellowBright.bold.inverse('💥 支持查询任何链的地址')
);
console.log(chalk.magenta.bold(`==============================================================`));
// 从控制台读取地址列表
async function getAddressesFromConsole() {
  const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout
  });

  console.log(chalk.cyan('📝 请输入钱包地址列表（每行一个地址，两次回车结束）：'));
  
  const addresses = [];
  
  return new Promise((resolve) => {
    const readAddress = () => {
      rl.question('', (input) => {
        const trimmedInput = input.trim();
        
        if (trimmedInput === '') {
          // 输入空行，结束输入
          rl.close();
          if (addresses.length === 0) {
            console.log(chalk.red('❌ 未输入任何地址，程序终止。'));
            process.exit(1);
          }
          console.log(chalk.green(`✅ 已输入 ${addresses.length} 个地址。\n`));
          resolve(addresses);
        } else {
          addresses.push(trimmedInput);
          readAddress();
        }
      });
    };
    
    readAddress();
  });
}

// 构建签名
function preHash(timestamp, method, request_path, params) {
  let query_string = '';
  if (method === 'GET' && params) {
    query_string = '?' + querystring.stringify(params);
  }
  return timestamp + method + request_path + query_string;
}

function sign(message, secret_key) {
  const hmac = crypto.createHmac('sha256', secret_key);
  hmac.update(message);
  return hmac.digest('base64');
}

function createSignature(method, request_path, params) {
  const timestamp = new Date().toISOString().slice(0, -5) + 'Z';
  const message = preHash(timestamp, method, request_path, params);
  const signature = sign(message, api_config.secret_key);
  return { signature, timestamp };
}

// 发送 GET 请求
function sendGetRequest(request_path, params, resultsForAddress, retryCount, callback) {
  const { signature, timestamp } = createSignature('GET', request_path, params);

  const headers = {
    'OK-ACCESS-KEY': api_config.api_key,
    'OK-ACCESS-SIGN': signature,
    'OK-ACCESS-TIMESTAMP': timestamp,
    'OK-ACCESS-PASSPHRASE': api_config.passphrase,
    'OK-ACCESS-PROJECT': api_config.project
  };

  const options = {
    hostname: 'www.okx.com',
    path: request_path + (params ? `?${querystring.stringify(params)}` : ''),
    method: 'GET',
    headers: headers
  };

  const req = https.request(options, (res) => {
    let data = '';
    res.on('data', (chunk) => {
      data += chunk;
    });
    res.on('end', () => {
      try {
        const parsedData = JSON.parse(data);
        if (parsedData.code === '0') {
          const totalValue = parseFloat(parsedData.data[0]?.totalValue || '0');
          if (!isNaN(totalValue)) {
            resultsForAddress.total += totalValue;
          } else {
            console.log(chalk.red(`❌  无效的资产值: ${JSON.stringify(parsedData)}`));
          }
          callback();
        } else {
          callback();
        }
      } catch (error) {
        console.log(chalk.red(`❌  解析失败: ${error.message}`));
        callback();
      }
    });
  });

  req.on('error', (error) => {
    console.log(chalk.red(`❌  请求失败: ${error.message}`));
    callback();
  });

  req.end();
}

// 批量查询地址资产
async function batchFetchAssets(addresses, chains) {
  const results = {};

  for (const address of addresses) {
    const resultsForAddress = { total: 0 };
    console.log(chalk.blue.bold(`🔍  查询地址: ${address}`));

    for (const chain of chains) {
      const params = {
        address: address,
        chains: chain.id,
        assetType: 0
      };

      await new Promise((resolve) => {
        sendGetRequest('/api/v5/wallet/asset/total-value-by-address', params, resultsForAddress, 3, resolve);
      });
    }

    results[address] = resultsForAddress.total;
    console.log(chalk.green.bold(`💲  该地址的资产估值为: ${resultsForAddress.total.toFixed(2)} `));
    await new Promise((resolve) => setTimeout(resolve, delayBetweenRequests));
  }

  console.log(chalk.greenBright.bold.inverse('\n🔆  所有地址查询完毕！整理成表格如下：'));
  const formattedResults = Object.entries(results).map(([address, balance]) => ({
    '钱包地址': address,
    '资产估值': balance.toFixed(2),
  }));
  console.table(formattedResults);
  const totalAssets = Object.values(results).reduce((sum, balance) => sum + balance, 0);
  console.log(chalk.magenta.bold(`💲  以上所有钱包地址的资产总和为: ${totalAssets.toFixed(2)}`));

  // 过滤余额大于0的地址，并输出到文件
  const caughtBalances = Object.entries(results)
    .filter(([address, balance]) => parseFloat(balance) > 0)
    .map(([address, balance]) => ({
      address: address,
      estimatedBalance: parseFloat(balance).toFixed(2)
    }));

  if (caughtBalances.length > 0) {
    const outputContent = JSON.stringify(caughtBalances, null, 2); // 转换为带缩进的 JSON 字符串
    const outputFile = path.join(__dirname, 'balances.json');
    try {
      require('fs').writeFileSync(outputFile, outputContent, { encoding: 'utf-8' }); // 使用 'w' 模式写入（覆盖）
      console.log(chalk.yellow(`\n✅ 已将余额大于0的地址输出到标准 JSON 文件: ${outputFile}\n`));
    } catch (error) {
      console.error(chalk.red.bold(`❌ 无法写入输出文件: ${error.message}\n`));
    }
  } else {
    console.log(chalk.yellow('⚠️ 没有余额大于0的地址需要输出。\n'));
  }
}

// 主函数
(async () => {
  try {
    // 从控制台读取地址列表
    const addresses = await getAddressesFromConsole();
    console.log(chalk.greenBright.bold.inverse(`⏳ 正在查询 ${chains.length} 条链的资产信息`));

    await batchFetchAssets(addresses, chains);
  } catch (error) {
    console.error(chalk.red.bold(`❌ 程序执行出错: ${error.message}`));
    process.exit(1);
  }
})();
