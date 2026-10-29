/* RECOEVO v3 · qué es cada pieza (fuente: lista de materiales y hoja de ingeniería del plan de fábrica v3, 29-oct-2026).
   Cada pieza: nodos del modelo 3D que la forman, ancla para el punto táctil, ícono de la marca y texto en lenguaje sencillo. */
window.PARTES = [
  {
    id: "tapa", nodos: ["G_tapa"], ancla: "A_tapa", icono: "olor",
    titulo: "Tapa con junta",
    corto: "Cierra la boca y no deja salir el olor.",
    texto: "Se abre para echar las cáscaras. Al cerrarla, una junta de caucho sella el borde y arriba guarda el filtro de carbón.",
    datos: ["PP virgen inyectado", "Junta EPDM perfil D en todo el borde", "Alojamiento para el filtro"]
  },
  {
    id: "filtro", nodos: ["G_filtro", "G_tapa_filtro"], ancla: "A_filtro", icono: "filtro",
    titulo: "Filtro de carbón y válvula",
    corto: "Atrapa el olor; deja salir los gases.",
    texto: "Una bolsita con 60 g de carbón activado absorbe el olor. La válvula de una vía deja salir el aire sin que entren moscas.",
    datos: ["60 g de carbón activado: dura 6 meses", "Válvula de silicona Ø20 mm", "Tapita del filtro a presión"]
  },
  {
    id: "gabinete", nodos: ["G_gabinete"], ancla: "A_gabinete", icono: "reciclado",
    titulo: "Gabinete",
    corto: "La carcasa: del tamaño de una caneca con pedal.",
    texto: "Contiene todo el mecanismo. Se inyecta en una sola pieza con plástico reciclado y el logo va en relieve.",
    datos: ["PP inyectado de 2,2 mm con nervios", "70 % plástico reciclado", "32 × 34 × 52 cm · ≈5 kg"]
  },
  {
    id: "puerta", nodos: ["G_puerta"], ancla: "A_puerta", icono: "seguro",
    titulo: "Puerta frontal",
    corto: "Da acceso al balde.",
    texto: "Se abre para sacar el balde una vez por semana. Su cierre de doble acción evita que la abran los niños.",
    datos: ["PP virgen inyectado", "Cierre de doble acción para niños", "Junta EPDM"]
  },
  {
    id: "balde", nodos: ["G_balde"], ancla: "A_balde", icono: "balde",
    titulo: "Balde de 10 L con bolsa",
    corto: "Recibe las tiras trituradas.",
    texto: "Lleva una bolsa verde compostable con cordón. Se llena en una semana: la bolsa sale lista para la ruta de orgánicos.",
    datos: ["10 litros · asa y aro para la bolsa", "Una bolsa por semana", "El equipo trae 5 bolsas"]
  },
  {
    id: "base", nodos: ["G_base"], ancla: "A_base", icono: "reciclado",
    titulo: "Base y bastidor de pedales",
    corto: "Sostiene el equipo y guía los pedales.",
    texto: "Es el zócalo del equipo. Por dentro tiene nervios que le dan rigidez y el eje donde giran los dos pedales.",
    datos: ["PP 70 % reciclado, con nervios", "Eje de pedales de acero Ø8 mm"]
  },
  {
    id: "pedal_der", nodos: ["G_pedal_der"], ancla: "A_pedal_der", icono: "pedal",
    titulo: "Pedal derecho · tritura",
    corto: "Con el pie se mueven las cuchillas.",
    texto: "Es una palanca 2:1: el pie baja 6 cm y la cremallera baja 3 cm. Cada pisada hace girar el eje de corte unos 143°.",
    datos: ["PP con 30 % de fibra de vidrio", "≈20 segundos de pedaleo al día", "Sin motor ni electricidad"]
  },
  {
    id: "pedal_izq", nodos: ["G_pedal_izq"], ancla: "A_pedal_izq", icono: "aserrin",
    titulo: "Pedal izquierdo · aserrín",
    corto: "Suelta una dosis de aserrín.",
    texto: "Cada pisada gira el dosificador y deja caer 40 mL de aserrín sobre lo triturado: absorbe la humedad y frena el olor.",
    datos: ["40 mL por pisada", "≈3 dosis al día"]
  },
  {
    id: "cremallera", nodos: ["G_cremallera"], ancla: "A_cremallera", icono: "flecha",
    titulo: "Cremallera de acero",
    corto: "Convierte el empuje del pie en giro.",
    texto: "Une el pedal derecho con el piñón. Al pisar baja 30 mm; al soltar, un resorte la sube otra vez.",
    datos: ["Acero de 4 mm cortado en láser", "Carrera de 30 mm", "Resorte de retorno"]
  },
  {
    id: "pinon", nodos: ["G_pinon"], ancla: "A_pinon", icono: "ciclo",
    titulo: "Piñón con trinquete",
    corto: "Como la rueda libre de una bicicleta.",
    texto: "Al pisar, el piñón arrastra el eje hacia adelante. Al soltar, las uñas del trinquete resbalan y el eje no se devuelve.",
    datos: ["Piñón M2 de 12 dientes", "Acero de 8 mm zincado", "Rueda de trinquete PA-GF + 2 uñas de acero"]
  },
  {
    id: "eje", nodos: ["G_eje"], ancla: "A_eje", icono: "cuchillas",
    titulo: "Eje con 13 cuchillas",
    corto: "Las cuchillas de gancho agarran la cáscara.",
    texto: "Trece cuchillas giran juntas, separadas por anillos de plástico, y arrastran la cáscara contra el peine fijo.",
    datos: ["Eje hexagonal inox 304 de 12 mm", "Cuchillas Ø56 × 2,5 mm de acero templado", "12 separadores de POM"]
  },
  {
    id: "peine", nodos: ["G_peine"], ancla: "A_peine", icono: "tiras",
    titulo: "Peine fijo",
    corto: "Corta la cáscara en tiras de ≈5 mm.",
    texto: "Sus 12 dedos quedan entre las cuchillas. Cuando la cuchilla pasa, la cáscara se corta contra el dedo como una tijera.",
    datos: ["Inox 304 de 2 mm, estampado", "Dedos de 5 mm en huecos de 5,6 mm"]
  },
  {
    id: "camara", nodos: ["G_camara"], ancla: "A_camara", icono: "seguro",
    titulo: "Cámara y tolva de corte",
    corto: "Lleva las cáscaras a las cuchillas.",
    texto: "La boca mide 12 × 10 cm y la tolva es profunda: caben las cáscaras, pero la mano no alcanza las cuchillas.",
    datos: ["PP con 30 % de fibra de vidrio", "Boca de 12 × 10 cm", "Bujes de POM para el eje"]
  },
  {
    id: "retenes", nodos: ["G_reten_izq", "G_reten_der"], ancla: "A_reten_der", icono: "check",
    titulo: "Retenes",
    corto: "Sellan el paso del eje.",
    texto: "Dos retenes de caucho evitan que los jugos de la comida se salgan por donde pasa el eje.",
    datos: ["Retenes de labio NBR 12 × 22 × 5 mm", "Uno a cada lado de la cámara"]
  },
  {
    id: "perilla", nodos: ["G_perilla"], ancla: "A_perilla", icono: "ciclo",
    titulo: "Perilla de reversa",
    corto: "Destraba el eje a mano.",
    texto: "Si algo duro se atasca, se gira la perilla hacia atrás y el eje se libera. Como no hay volante ni motor, nada empuja solo.",
    datos: ["En el extremo izquierdo del eje", "Pieza inyectada"]
  },
  {
    id: "deposito", nodos: ["G_deposito"], ancla: "A_deposito", icono: "aserrin",
    titulo: "Depósito de aserrín y dosificador",
    corto: "Guarda el aserrín y lo dosifica.",
    texto: "Tiene 2 litros, suficientes para unos 16 días. El dosificador rotativo suelta una celda de 40 mL con cada pisada.",
    datos: ["2 L ≈ 16 días", "Dosificador rotativo de 40 mL", "Se recarga por una tapita arriba"]
  },
  {
    id: "seguro", nodos: ["G_seguro"], ancla: "A_seguro", icono: "seguro",
    titulo: "Seguro de tapa",
    corto: "Con la tapa abierta, el pedal no baja.",
    texto: "Al abrir la tapa, un pasador baja y bloquea la cremallera. Así las cuchillas no se mueven mientras alguien echa las cáscaras.",
    datos: ["Pasador inyectado con resorte", "Se validará con 20.000 ciclos"]
  },
  {
    id: "patas", nodos: ["G_patas"], ancla: "A_patas", icono: "check",
    titulo: "Patas antideslizantes",
    corto: "El equipo no se corre al pisar.",
    texto: "Cuatro patas de caucho termoplástico lo mantienen firme sobre el piso de la cocina.",
    datos: ["TPE inyectado · 4 patas"]
  }
];

/* Desplazamientos de la vista separada (metros, ejes de Blender: x derecha, y fondo, z arriba). Iguales al video. */
window.SEPARAR = {
  horizontal: {
    G_tapa: [0, 0.02, 0.56], G_gabinete: [0, 0.04, 0.42], G_puerta: [-0.44, -0.30, -0.02, -0.45], G_balde: [0, -0.34, -0.12],
    G_base: [0, 0.02, -0.20], G_patas: [0, 0.02, -0.28], G_pedal_der: [0.32, -0.16, -0.14], G_pedal_izq: [-0.30, -0.16, -0.16],
    G_deposito: [-0.42, 0.02, 0.02, 0.3], G_camara: [0, 0, 0.04], G_seguro: [0.30, -0.05, 0.14], G_peine: [0, -0.22, -0.07],
    G_eje: [0, -0.13, -0.02], G_perilla: [-0.24, -0.13, -0.02], G_reten_izq: [-0.075, -0.13, -0.02], G_reten_der: [0.075, -0.13, -0.02],
    G_pinon: [0.17, -0.13, -0.02], G_cremallera: [0.34, -0.10, -0.06],
    G_tapa_filtro: [0, 0, 0.085], G_filtro: [0, 0, 0.045],
    G_pata0: [0.035, 0.035, 0], G_pata1: [-0.035, 0.035, 0], G_pata2: [0.035, -0.035, 0], G_pata3: [-0.035, -0.035, 0]
  },
  vertical: {
    G_tapa: [0, 0.02, 0.64], G_gabinete: [0, 0.04, 0.47], G_puerta: [-0.25, -0.30, -0.07, -0.45], G_balde: [0, -0.34, -0.17],
    G_base: [0, 0.02, -0.27], G_patas: [0, 0.02, -0.37], G_pedal_der: [0.19, -0.16, -0.21], G_pedal_izq: [-0.19, -0.16, -0.23],
    G_deposito: [-0.27, 0.02, 0.05, 0.3], G_camara: [0, 0, 0.06], G_seguro: [0.20, -0.05, 0.18], G_peine: [0, -0.22, -0.07],
    G_eje: [0, -0.13, 0], G_perilla: [-0.17, -0.13, 0], G_reten_izq: [-0.06, -0.13, 0], G_reten_der: [0.06, -0.13, 0],
    G_pinon: [0.12, -0.13, 0], G_cremallera: [0.23, -0.10, -0.09],
    G_tapa_filtro: [0, 0, 0.085], G_filtro: [0, 0, 0.045],
    G_pata0: [0.035, 0.035, 0], G_pata1: [-0.035, 0.035, 0], G_pata2: [0.035, -0.035, 0], G_pata3: [-0.035, -0.035, 0]
  }
};

/* Recorrido «Cómo funciona» (pasos con su texto). */
window.PASOS = [
  { id: "tapa", texto: "1 · Abres la tapa y echas las cáscaras." },
  { id: "pedal_der", texto: "2 · Cierras y pisas el pedal derecho: 13 cuchillas las cortan en tiras." },
  { id: "pedal_izq", texto: "3 · Con el pedal izquierdo cae una dosis de aserrín." },
  { id: "balde", texto: "4 · Abajo, un balde de 10 L con bolsa compostable: una por semana." }
];
