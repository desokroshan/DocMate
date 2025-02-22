<!-- <template> -->
  <!-- <div class="about"> -->
    <!-- <h1>This is an about page</h1> -->
    <!-- <iframe src="https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d2688.094682452945!2d-122.13381028784576!3d47.64372688529268!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x54906d0048713c8d%3A0xf54a3d953253f8c9!2sMicrosoft%20Reactor%20Redmond!5e0!3m2!1sen!2sus!4v1740257940457!5m2!1sen!2sus" width="100%" height="600" style="border:0;" allowfullscreen="" loading="lazy" referrerpolicy="no-referrer-when-downgrade"></iframe> -->
  <!-- </div> -->
<!-- </template> -->

<!-- <style>
@media (min-width: 1024px) {
  .about {
    min-height: 100vh;
    display: flex;
    align-items: center;
  }
}
</style> -->


<template>
  <div class="chat-container">
    <div class="chat-display">
      <div v-for="(message, index) in messages" :key="index" class="chat-message">
        <p><strong>You:</strong> {{ message.prompt }}</p>
        <p><strong>DocMate:</strong> {{ message.response }}</p>
      </div>
    </div>
    <div class="chat-input">
      <input v-model="userInput" type="text" placeholder="Type your message..." @keyup.enter="sendMessage" />
      <button @click="sendMessage">Enter</button>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      userInput: "",
      messages: []
    };
  },
  methods: {
    async sendMessage() {
      if (this.userInput.trim() === "") return;
      
      const userPrompt = this.userInput;
      this.userInput = "";
      
      // Make an actual HTTP POST request
      const response = await this.fetchResponse(userPrompt);
      
      this.messages.unshift({ prompt: userPrompt, response });
    },
    async fetchResponse(prompt) {
      // Simulated API response, replace with actual API call
      return new Promise((resolve) => {
        setTimeout(() => resolve(`Sorry, I don't have knowledge about ${prompt}.`), 1000);
      });
    //   try {
    //     const response = await fetch("http://localhost:9000/fetch/", {
    //       method: "POST",
    //       headers: {
    //         "Content-Type": "application/json"
    //       },
    //       body: JSON.stringify({ prompt })
    //     });
    //     const data = await response.json();
    //     return data.response || "No response from server";
    //   } catch (error) {
    //     return "Error fetching response";
    //   }
    }
  }
};
</script>

<style scoped>
.chat-container {
  display: flex;
  flex-direction: column;
  width: 40vw;
  height: 90vh;
  margin: 5vh auto;
  padding: 20px;
  border: 1px solid #ccc;
  border-radius: 5px;
  background-color: #f9f9f9;
}
.chat-display {
  flex: 1;
  overflow-y: auto;
  margin-bottom: 10px;
  border-bottom: 1px solid #ccc;
  padding: 10px;
}
.chat-message {
  margin-bottom: 10px;
}
.chat-input {
  display: flex;
  gap: 10px;
}
.chat-input input {
  flex: 1;
  padding: 5px;
}
.chat-input button {
  padding: 5px 10px;
}
</style>

