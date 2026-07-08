import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import Qt5Compat.GraphicalEffects

Item {
    Layout.fillWidth: true
    Layout.fillHeight: true

    ColumnLayout {
        anchors.fill: parent
        spacing: 0

        // 1. Banner superior: Imagen que sirve como fondo para texto(s)
        Item {
            id: bannerItem
            Layout.fillWidth: true
            Layout.preferredHeight: 110 // Ajusta la altura del banner como desees
            Layout.margins: 10 // Margen para que destaquen los bordes redondeados

            layer.enabled: true
            layer.effect: OpacityMask {
                maskSource: Rectangle {
                    width: bannerItem.width
                    height: bannerItem.height
                    radius: 12
                }
            }

            Image {
                anchors.fill: parent
                source: "assets/hero-featured.jpg"
                fillMode: Image.PreserveAspectCrop // La imagen recubre toda el área

                // Opcional: Oscurecer un poco la imagen para que el texto resalte mejor
                Rectangle {
                    anchors.fill: parent
                    color: "#99000000" // Negro al 60%
                }
            }

            // Aquí puedes agregar más elementos de texto o centrarlos
            Column {
                anchors.centerIn: parent
                spacing: 15

                Text {
                    text: "Your Apps"
                    color: "#ff6942"
                    font.pixelSize: 32
                    font.bold: true
                    horizontalAlignment: Text.AlignHCenter
                }

                Text {
                    text: "Find enternainment, browsers and more"
                    color: "#888b94"
                    font.pixelSize: 18
                    horizontalAlignment: Text.AlignHCenter
                }
            }
        }

        // 2. Grilla / Grid inferior usando Flow para que los elementos fluyan (envoltorio responsivo)
        ScrollView {
            id: appsScrollView
            Layout.fillWidth: true
            Layout.fillHeight: true
            clip: true
            contentWidth: availableWidth // Evita que el contenedor crezca horizontalmente
            ScrollBar.horizontal.policy: ScrollBar.AlwaysOff // Desactiva el scroll horizontal

            Flow {
                width: appsScrollView.availableWidth // Toma el ancho disponible real, forzando a que bajen los elementos
                spacing: 20
                padding: 20

                // Model de prueba con apps y categorías
                Repeater {
                    model: ListModel {
                        ListElement { title: "Retroarch"; category: "Emulation"; command: "retroarch"; img: "assets/retroarch.png" }
                        ListElement { title: "Steamlink"; category: "Game Streaming"; command: "steamlink"; img: "assets/steamlink.jpeg" }
                        ListElement { title: "Moonlight"; category: "Game Streaming"; command: "moonlight-qt"; img: "assets/moonlight.jpeg" }
                    }

                    // Componente Card para cada app
                    Item { // Usamos un Item envoltorio para habilitar OpacityMask
                        id: cardItem
                        width: 220
                        height: 240
                        
                        layer.enabled: true
                        layer.effect: OpacityMask {
                            maskSource: Rectangle {
                                width: cardItem.width
                                height: cardItem.height
                                radius: 8
                            }
                        }

                        Rectangle {
                            anchors.fill: parent
                            color: "#252525" // Fondo gris oscuro de la card
                            // Ya no necesitamos aplicar radius individual aquí gracias a la máscara

                            MouseArea {
                                anchors.fill: parent
                                onClicked: backend.launch_app(model.command)
                                cursorShape: Qt.PointingHandCursor
                            }

                            ColumnLayout {
                                anchors.fill: parent
                                spacing: 0

                                // Imagen específica de la cap (hardcodeada por ahora)
                                Image {
                                    Layout.fillWidth: true
                                    Layout.preferredHeight: 140
                                    source: model.img
                                    fillMode: Image.PreserveAspectCrop
                                }

                                // Sección inferior de la tarjeta con título e info
                                Item {
                                    Layout.fillWidth: true
                                    Layout.fillHeight: true

                                    Column {
                                        anchors.fill: parent
                                        anchors.margins: 15
                                        spacing: 5

                                        Text {
                                            text: model.title
                                            color: "#FFFFFF"
                                            font.pixelSize: 20
                                            font.bold: true
                                        }

                                        Text {
                                            text: model.category
                                            color: "#AAAAAA"
                                            font.pixelSize: 14
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    }
}
