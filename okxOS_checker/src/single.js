const crypto = require('crypto');
const https = require('https');
const querystring = require('querystring');
const chalk = require('chalk');
const fs = require('fs');
const path = require('path');
const Table = require('cli-table3');
const readline = require('readline');
require('dotenv').config({ path: path.resolve(__dirname, '../.env') });

// 配置常量
const CONFIG = {
    API_BASE_URL: 'www.okx.com',
    REQUEST_DELAY: 100, // 请求间隔（毫秒）
    MAX_RETRIES: 3,     // 最大重试次数
    TIMEOUT: 10000      // 请求超时时间（毫秒）
};

// API配置验证
const api_config = {
    api_key: process.env.OKX_API_KEY,
    secret_key: process.env.OKX_SECRET_KEY,
    passphrase: process.env.OKX_PASSPHRASE,
    project: process.env.OKX_PROJECT
};

// 验证API配置
function validateApiConfig() {
    const requiredFields = ['api_key', 'secret_key', 'passphrase', 'project'];
    const missingFields = requiredFields.filter(field => !api_config[field]);
    
    if (missingFields.length > 0) {
        throw new Error(`缺少必要的API配置: ${missingFields.join(', ')}`);
    }
}

// 工具函数
class Utils {
    static delay(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    static preHash(timestamp, method, request_path, params) {
        let query_string = '';
        if (method === 'GET' && params) {
            query_string = '?' + querystring.stringify(params);
        }
        return timestamp + method + request_path + query_string;
    }

    static sign(message, secret_key) {
        const hmac = crypto.createHmac('sha256', secret_key);
        hmac.update(message);
        return hmac.digest('base64');
    }

    static createSignature(method, request_path, params) {
        const timestamp = new Date().toISOString().slice(0, -5) + 'Z';
        const message = this.preHash(timestamp, method, request_path, params);
        const signature = this.sign(message, api_config.secret_key);
        return { signature, timestamp };
    }

    static validateAddress(address) {
        if (!address || typeof address !== 'string' || address.trim().length === 0) {
            throw new Error('请提供有效的钱包地址');
        }
        return address.trim();
    }

    static formatCurrency(value) {
        return parseFloat(value).toFixed(2);
    }
}

// API请求类
class OkxApiClient {
    constructor() {
        this.baseUrl = CONFIG.API_BASE_URL;
    }

    async makeRequest(request_path, params, chainName, retryCount = 0) {
        const { signature, timestamp } = Utils.createSignature("GET", request_path, params);

        const headers = {
            'OK-ACCESS-KEY': api_config.api_key,
            'OK-ACCESS-SIGN': signature,
            'OK-ACCESS-TIMESTAMP': timestamp,
            'OK-ACCESS-PASSPHRASE': api_config.passphrase,
            'OK-ACCESS-PROJECT': api_config.project,
            'Content-Type': 'application/json'
        };

        const options = {
            hostname: this.baseUrl,
            path: request_path + (params ? `?${querystring.stringify(params)}` : ''),
            method: 'GET',
            headers: headers,
            timeout: CONFIG.TIMEOUT
        };

        return new Promise((resolve, reject) => {
            const req = https.request(options, (res) => {
                let data = '';
                
                res.on('data', (chunk) => {
                    data += chunk;
                });
                
                res.on('end', () => {
                    try {
                        const parsedData = JSON.parse(data);
                        
                        if (parsedData.code === '0') {
                            resolve(parsedData);
                        } else {
                            const error = new Error(`API错误: ${parsedData.msg || '未知错误'}`);
                            error.code = parsedData.code;
                            reject(error);
                        }
                    } catch (error) {
                        reject(new Error(`数据解析失败: ${error.message}`));
                    }
                });
            });

            req.on('error', (error) => {
                reject(new Error(`网络请求失败: ${error.message}`));
            });

            req.on('timeout', () => {
                req.destroy();
                reject(new Error('请求超时'));
            });

            req.end();
        });
    }

    async getAssetValue(address, chainId, chainName) {
        const request_path = '/api/v5/wallet/asset/total-value-by-address';
        const params = {
            address: address,
            chains: chainId,
            assetType: 0
        };

        for (let retry = 0; retry < CONFIG.MAX_RETRIES; retry++) {
            try {
                const response = await this.makeRequest(request_path, params, chainName);
                const totalValue = parseFloat(response.data[0]?.totalValue || '0');
                return { success: true, value: totalValue };
            } catch (error) {
                if (retry === CONFIG.MAX_RETRIES - 1) {
                    console.error(chalk.red(`❌  链 ${chainName} 查询失败: ${error.message}`));
                    return { success: false, value: 0, error: error.message };
                }
                await Utils.delay(1000 * (retry + 1)); // 指数退避
            }
        }
    }
}

// 结果处理类
class ResultProcessor {
    constructor() {
        this.results = { total: 0, chains: [] };
        this.table = new Table({
            head: [chalk.cyan('链名称'), chalk.cyan('资产估值')],
            style: { head: ['green'], border: ['yellow'] }
        });
    }

    addResult(chainName, value) {
        if (value > 0) {
            this.table.push([chalk.green(chainName), chalk.yellow(Utils.formatCurrency(value))]);
            this.results.total += value;
            this.results.chains.push({ name: chainName, value });
        }
    }

    displayResults(address) {        
        console.log(chalk.greenBright.bold.inverse(`\n🔆  查询完毕！各链资产余额如下：`));
        console.log(chalk.green.bold(`🔍  查询地址: ${address}`));
        if (this.results.chains.length > 0) {
            console.log(this.table.toString());
            console.log(chalk.cyan(`📊  持有资产的链数量: ${this.results.chains.length}`));
            console.log(chalk.magenta.bold(`💲  总资产估值: ${Utils.formatCurrency(this.results.total)}\n`));  
        } else {
            console.log(chalk.yellow.bold('\n⚠️  未找到任何资产估值大于 0 的链\n'));
        }

        // 过滤余额大于0的地址，并输出到文件
        const caughtBalances = this.results.chains
            .filter(chain => parseFloat(chain.value) > 0)
            .map(chain => ({
                address: address,
                chainName: chain.name,
                estimatedBalance: parseFloat(chain.value).toFixed(2)
            }));

        if (caughtBalances.length > 0) {
            const outputContent = JSON.stringify(caughtBalances, null, 2); // 转换为带缩进的 JSON 字符串
            const outputFile = path.join(__dirname, 'balances.json');
            try {
                require('fs').writeFileSync(outputFile, outputContent, { encoding: 'utf-8' }); // 使用 'w' 模式写入（覆盖）
                console.log(chalk.yellow(`✅ 已将余额大于0的地址输出到标准 JSON 文件: ${outputFile}\n`));
            } catch (error) {
                console.error(chalk.red.bold(`❌ 无法写入输出文件: ${error.message}\n`));
            }
        } else {
            console.log(chalk.yellow('⚠️ 没有余额大于0的地址需要输出。\n'));
        }
    }
}

// 主程序类
class WalletChecker {
    constructor() {
        this.apiClient = new OkxApiClient();
        this.resultProcessor = new ResultProcessor();
    }

    async loadChains() {
        const chainsPath = path.resolve(__dirname, '../chains.json');
        try {
            const data = fs.readFileSync(chainsPath, 'utf-8');
            return JSON.parse(data);
        } catch (error) {
            throw new Error(`无法加载链列表: ${error.message}`);
        }
    }

    async processAddress(address) {
        try {
            const chains = await this.loadChains();
            console.log(chalk.greenBright.bold.inverse(`\n⏳  正在查询 ${chains.length} 条链的资产信息`));

            for (const chain of chains) {
                const result = await this.apiClient.getAssetValue(address, chain.id, chain.name);
                if (result.success) {
                    this.resultProcessor.addResult(chain.name, result.value);
                }
                await Utils.delay(CONFIG.REQUEST_DELAY);
            }

            this.resultProcessor.displayResults(address);
        } catch (error) {
            console.error(chalk.red.bold(`❌  处理失败: ${error.message}`));
            throw error;
        }
    }

    async run() {
        try {
            validateApiConfig();
            
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
  chalk.yellowBright.bold.inverse('💥 单个钱包各链资产余额查询工具') + '       ' +
  chalk.yellowBright.bold.inverse('💥 支持查询任何链的地址')
);
console.log(chalk.magenta.bold(`==============================================================`));
            
            const rl = readline.createInterface({
                input: process.stdin,
                output: process.stdout
            });

            const address = await new Promise((resolve) => {
                rl.question(chalk.green('✍️  请输入查询的钱包地址: '), (input) => {
                    rl.close();
                    resolve(input);
                });
            });

            const validatedAddress = Utils.validateAddress(address);
            await this.processAddress(validatedAddress);

        } catch (error) {
            console.error(chalk.red.bold(`❌  程序执行失败: ${error.message}`));
            process.exit(1);
        }
    }
}

// 启动程序
if (require.main === module) {
    const checker = new WalletChecker();
    checker.run().catch(error => {
        console.error(chalk.red.bold(`❌  程序异常退出: ${error.message}`));
        process.exit(1);
    });
}

module.exports = { WalletChecker, OkxApiClient, Utils };
