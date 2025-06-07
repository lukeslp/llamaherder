# Code Snippets from toollama/styles/animations.css

File: `toollama/styles/animations.css`  
Language: CSS  
Extracted: 2025-06-07 05:10:18  

## Snippet 1
Lines 12-22

```CSS
@keyframes slide {
  from {
    opacity: 0;
    transform: translate(var(--slide-x, 0), var(--slide-y, 100%));
  }
  to {
    opacity: 1;
    transform: translate(0);
  }
}
```

## Snippet 2
Lines 42-56

```CSS
@keyframes futuristicGlow {
  0% {
    filter: blur(8px) brightness(1);
    opacity: 0.5;
  }
  50% {
    filter: blur(12px) brightness(1.2);
    opacity: 0.6;
  }
  100% {
    filter: blur(8px) brightness(1);
    opacity: 0.5;
  }
}
```

## Snippet 3
Lines 65-81

```CSS
/* Gradient animation base classes */
.gradient-animate {
  background-size: 200% 200%;
  animation: gradientRotate 15s ease infinite;
}

.gradient-border-animate {
  background-origin: border-box;
  background-size: 200% 200%;
  animation: gradientFlow 15s ease infinite;
}

.gradient-border-rotate {
  border: 2px solid transparent;
  background-origin: border-box;
  animation: gradientBorder 10s ease infinite;
}
```

