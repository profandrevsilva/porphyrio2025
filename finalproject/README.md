
---

# ✅ **1. Estrutura Geral do Projeto**

* **Micro:bit emissor** → Fica no protótipo com o sensor ultrassônico + shield.
  → Detecta presença e envia mensagem por rádio.

* **Micro:bit receptor (professor)** → Recebe a mensagem e dispara um alerta (som/LED).

* **Suporte físico** → Construído pela equipe com material não estruturado (papelão, EVA, garrafa PET, etc).

---

# 🎯 **2. O que o grupo precisa entregar**

✔ Protótipo físico com sensor ultrassônico + micro:bit emissor
✔ Micro:bit do professor com código receptor
✔ Dois códigos (emissor + receptor)
✔ Explicação no pitch:

* Como escolheu as distâncias
* Como configurou o rádio
* Qual alerta criou
* Justificativa do design do suporte

---

# 🛠️ **3. CÓDIGO DO MICRO:BIT EMISSOR (com sensor ultrassônico)**

➡ Este ficará no **protótipo**.

Use no MakeCode:

```blocks
radio.setGroup(15) // grupo escolhido pela equipe

basic.forever(function () {
    // Mede a distância usando o sensor
    let distancia = sonar.ping(
        DigitalPin.P0,
        DigitalPin.P1,
        PingUnit.Centimeters
    )
    
    // Escolha da equipe (exemplo: 60 cm)
    if (distancia < 60 && distancia != 0) {
        radio.sendString("PRESENÇA")
        basic.showIcon(IconNames.Happy)
    } else {
        basic.clearScreen()
    }
    
    basic.pause(300)
})
```

📌 **Pontos importantes:**

* Grupo pode alterar a distância (ex.: 40 cm, 50 cm, etc).
* Ícone pode ser outro (coração, alerta, etc).
* Grupo escolhe o **número do rádio** (ex.: 15).

---

# 📡 **4. CÓDIGO DO MICRO:BIT RECEPTOR (professor)**

```blocks
radio.setGroup(15)

radio.onReceivedString(function (msg) {
    if (msg == "PRESENÇA") {
        basic.showIcon(IconNames.Surprised)
        music.playTone(880, 200)
        music.playTone(880, 200)
    }
})

basic.forever(function () {
    // Pode adicionar LED sempre ligado, se quiser
})
```

📌 A equipe pode criar alertas diferentes:

* Som customizado
* Animação no display
* Texto rolando (ex.: “ALGUÉM ENTROU!”)

---

# 🧩 **5. Ideias de Suporte Criativo (material não estruturado)**

🎨 A criatividade **conta pontos** — então aqui estão sugestões:

### **a) Porta automática de papelão**

* Micro:bit fica escondido dentro de uma “caixa” simulando uma porta.
* Sensor fica apontado para fora.

### **b) “Robô sentinela”**

* Corpo feito de caixa de sapato
* Olhos = sensor ultrassônico
* Micro:bit como "coração" na frente

### **c) Totem de segurança**

* Garrafa PET cortada e forrada com EVA
* Sensor fica na “janela” frontal
* Micro:bit fica como painel luminoso

### **d) Caixa de correio futurista**

* Papelão pintado como equipamento de segurança
* Micro:bit mostra símbolos de alerta

---

# ⚙️ **6. Shield e Conexões**

Usar o **shield** facilita:

* Normalmente o TRIG vai para P0
* O ECHO vai para P1
* O shield já cuida do nível de tensão do HC-SR04 (5V → 3.3V)

Se não tiver shield:

* TRIG → P0
* ECHO → P1 (com divisor de tensão!!)
* VCC → 5V
* GND → GND

---

# 🎤 **7. Roteiro de Pitch (modelo para o grupo)**

Duração ideal: **1 minuto**

### **1. Problema real**

> “Na sala de aula é difícil saber quando alguém está se aproximando ou entrando, especialmente durante atividades. Criamos um protótipo de sensor de presença inteligente que detecta aproximação e envia um alerta ao professor.”

### **2. Solução proposta**

> “Usamos dois micro:bits: um com sensor ultrassônico (emissor) e outro com alerta sonoro e visual (receptor).”

### **3. Como funciona**

> “Quando alguém chega a menos de *X* centímetros, o emissor envia via rádio a palavra *‘PRESENÇA’* e o micro:bit do professor dá um alerta.”

### **4. Escolhas do grupo**

* Distância escolhida: **X cm** (justificar)
* Alerta escolhido: som, animação, símbolo, etc
* Design do suporte: por quê escolhemos esse formato?

### **5. Conclusão**

> “Nosso projeto demonstra automação simples, comunicação sem fio e design criativo aplicado a uma situação real.”

---

# ✔️ Se quiser, posso criar:

🛠️ **um PDF completo com relatório final**
📐 **desenho do protótipo**
📦 **lista de materiais personalizada**
🎤 **um pitch pronto para apresentar**

É só pedir!
