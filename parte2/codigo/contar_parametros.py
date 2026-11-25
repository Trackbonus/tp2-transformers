from transformers import AutoModelForSequenceClassification

model = AutoModelForSequenceClassification.from_pretrained(
    "distilbert-base-uncased",
    num_labels=1
)

total = sum(p.numel() for p in model.parameters())
trainable = sum(p.numel() for p in model.parameters() if p.requires_grad)

print("Total:", f"{total:,}")
print("Entrenables:", f"{trainable:,}")
print("% entrenable:", f"{100 * trainable / total:.2f}%")