const { MongoClient } = require('mongodb');

const uri = "mongodb+srv://themodelhq:<db_password>@cluster0.gn037.mongodb.net/?retryWrites=true&w=majority";

const client = new MongoClient(uri, {
  useNewUrlParser: true,
  useUnifiedTopology: true,
  tls: true
});

async function testConnection() {
  try {
    await client.connect();
    console.log("Connected successfully to MongoDB!");
  } catch (error) {
    console.error("Connection failed:", error);
  } finally {
    await client.close();
  }
}

testConnection();
