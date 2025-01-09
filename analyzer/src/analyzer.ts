import "dotenv/config"
import { connect, JSONCodec } from "nats";



function getEnvVars(names: string[]): Record<string, string> {
    return names.reduce((envVars, name) => {
        const value = process.env[name];
        if (!value) throw new Error(`Missing required environment variable: ${name}`);
        envVars[name] = value;
        return envVars;
    }, {} as Record<string, string>);
}

const envVars = getEnvVars(['NATS_SERVER', 'NATS_SUBJECT']);




const nc = await connect({ servers: envVars["NATS_SERVER"] });

const jc = JSONCodec();

const sub = nc.subscribe(envVars["NATS_SUBJECT"]);
(async () => {
    for await (const m of sub) {
        const jsonData = jc.decode(m.data);
        console.log(`[${sub.getProcessed()}]:`, jsonData);
    }
    console.log("subscription closed");
})();

await nc.drain();