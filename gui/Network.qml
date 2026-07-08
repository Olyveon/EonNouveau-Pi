import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Item {
    id: networkRoot
    Layout.fillWidth: true
    Layout.fillHeight: true

    property string selectedNetwork: ""
    property string currentConnectedSsid: ""
    property bool isScanning: true

    Component.onCompleted: {
        // Al cargar la pestaña, pedimos a Python que busque los datos
        networkBackend.request_status()
        networkBackend.scan_networks()
    }

    Connections {
        target: networkBackend

        function onNetworks_ready(networksJson) {
            var netList = JSON.parse(networksJson);
            networkModel.clear();
            for (var i = 0; i < netList.length; i++) {
                networkModel.append(netList[i]);
            }
            isScanning = false;
        }

        function onConnection_status(icon, ssid, ip) {
            currentIcon.text = icon;
            currentSsid.text = "Conectado a: " + ssid;
            currentConnectedSsid = ssid;
            currentIp.text = "Dirección IP: " + ip;
        }

        function onConnect_result(success, message) {
            // Mostrar error o éxito
            if (!success) {
                errorTextPopup.text = message;
                errorPopup.open();
            }
        }
    }

    ColumnLayout {
        anchors.fill: parent
        spacing: 20

        // Current Connection Info
        Rectangle {
            Layout.fillWidth: true
            Layout.preferredHeight: 100
            color: "#191723"
            radius: 10
            border.color: "#25282c"
            border.width: 2

            RowLayout {
                anchors.fill: parent
                anchors.margins: 20
                spacing: 20

                Text {
                    id: currentIcon
                    text: "🚫"
                    font.pixelSize: 40
                    color: "#fc724f"
                }

                ColumnLayout {
                    Layout.fillWidth: true
                    spacing: 5
                    Text { id: currentSsid; text: "Cargando..."; color: "#FFFFFF"; font.pixelSize: 18; font.bold: true }
                    Text { id: currentIp; text: "Dirección IP: --"; color: "#8a8d94"; font.pixelSize: 14 }
                }
                
                Button {
                    text: (currentConnectedSsid !== "Sin conexión" && currentConnectedSsid !== "Error de red") ? "Olvidar" : "Desconectar"
                    background: Rectangle { color: "#331f1f"; radius: 8; border.color: "#501617"; border.width: 2 }
                    contentItem: Text { text: parent.text; color: "#fc724f"; horizontalAlignment: Text.AlignHCenter; verticalAlignment: Text.AlignVCenter }
                    Layout.preferredWidth: 110
                    Layout.preferredHeight: 40
                    onClicked: {
                        if (text === "Olvidar") {
                            networkBackend.forget_network(currentConnectedSsid)
                        } else {
                            networkBackend.disconnect_network()
                        }
                    }
                }
            }
        }

        RowLayout {
            Layout.fillWidth: true
            Layout.topMargin: 10
            
            Text {
                text: isScanning ? "Buscando Redes..." : "Redes Disponibles"
                color: "#FFFFFF"
                font.pixelSize: 22
                font.bold: true
                Layout.fillWidth: true
            }

            Button {
                text: "↻ Refrescar"
                background: Rectangle { color: "transparent" }
                contentItem: Text { text: parent.text; color: "#fc724f"; font.pixelSize: 16 }
                onClicked: {
                    isScanning = true;
                    networkModel.clear();
                    networkBackend.scan_networks();
                }
            }
        }

        // Available Networks List
        Rectangle {
            Layout.fillWidth: true
            Layout.fillHeight: true
            color: "transparent"

            ListView {
                id: networksList
                anchors.fill: parent
                clip: true
                spacing: 12
                ScrollBar.vertical: ScrollBar { policy: ScrollBar.AlwaysOff }

                model: ListModel { id: networkModel }

                delegate: Rectangle {
                    width: ListView.view.width
                    height: 70
                    color: "#191723"
                    radius: 10
                    border.color: hoverArea.containsMouse ? "#fc724f" : "#25282c"
                    border.width: hoverArea.containsMouse ? 2 : 1

                    MouseArea {
                        id: hoverArea
                        anchors.fill: parent
                        hoverEnabled: true
                        onClicked: {
                            selectedNetwork = model.ssid
                            if (model.known) {
                                // Si ya se conoce, conectar directamente usando el perfil guardado
                                networkBackend.connect_network(model.ssid, "")
                            } else if (model.secured) {
                                passwordInput.text = ""
                                passwordPopup.open()
                            } else {
                                networkBackend.connect_network(model.ssid, "")
                            }
                        }
                    }

                    RowLayout {
                        anchors.fill: parent
                        anchors.margins: 15
                        spacing: 15

                        Text {
                            text: model.known ? "⭐" : (model.secured ? "🔒" : "🔓")
                            font.pixelSize: 20
                            color: model.known ? "#fc724f" : "#8a8d94"
                        }

                        Text {
                            text: model.ssid
                            color: "#FFFFFF"
                            font.pixelSize: 18
                            Layout.fillWidth: true
                        }

                        Text {
                            text: "Señal: " + model.strength
                            color: "#8a8d94"
                            font.pixelSize: 14
                        }
                        
                        Button {
                            id: connectBtn
                            text: model.known ? "Olvidar" : "Conectar"
                            background: Rectangle { 
                                color: "#191723"
                                radius: 5 
                                border.color: model.known ? "#8a8d94" : "#fc724f"
                                border.width: 1 
                            }
                            contentItem: Text { 
                                text: connectBtn.text
                                color: model.known ? "#8a8d94" : "#fc724f"
                                horizontalAlignment: Text.AlignHCenter 
                                verticalAlignment: Text.AlignVCenter 
                            }
                            Layout.preferredWidth: 90
                            Layout.preferredHeight: 35
                            onClicked: {
                                selectedNetwork = model.ssid
                                if (model.known) {
                                    networkBackend.forget_network(model.ssid)
                                } else if (model.secured) {
                                    passwordInput.text = ""
                                    passwordPopup.open()
                                } else {
                                    networkBackend.connect_network(model.ssid, "")
                                }
                            }
                        }
                    }
                }
            }
        }
    }

    // Popup para ingresar contraseña
    Popup {
        id: passwordPopup
        width: 800
        height: 230
        x: Math.round((parent.width - width) / 2)
        y: -20 // Posicionado arriba para no estorbar con el teclado virtual
        z: 1
        modal: true
        focus: true
        closePolicy: Popup.CloseOnEscape | Popup.CloseOnPressOutside

        background: Rectangle {
            color: "#0b0d13"
            radius: 15
            border.color: "#fc724f"
            border.width: 2
        }

        ColumnLayout {
            anchors.fill: parent
            anchors.margins: 25
            spacing: 15

            Text {
                text: "Conectar a " + selectedNetwork
                color: "#FFFFFF"
                font.pixelSize: 20
                font.bold: true
                Layout.alignment: Qt.AlignHCenter
            }

            TextField {
                id: passwordInput
                Layout.fillWidth: true
                Layout.preferredHeight: 50
                placeholderText: "Contraseña de red"
                echoMode: showPassword ? TextInput.Normal : TextInput.Password
                color: "#FFFFFF"
                font.pixelSize: 16
                placeholderTextColor: "#8a8d94"
                rightPadding: 50
                
                property bool showPassword: false

                background: Rectangle {
                    color: "#191723"
                    radius: 8
                    border.color: passwordInput.activeFocus ? "#fc724f" : "#25282c"
                    border.width: 2
                }

                // Botón de ojo para mostrar/ocultar contraseña
                Text {
                    id: eyeIcon
                    anchors.right: parent.right
                    anchors.rightMargin: 15
                    anchors.verticalCenter: parent.verticalCenter
                    text: passwordInput.showPassword ? "ʘ" : "◡"
                    font.pixelSize: 22
                    color: passwordInput.showPassword ? "#fc724f" : "#8a8d94"
                    
                    MouseArea {
                        anchors.fill: parent
                        onClicked: passwordInput.showPassword = !passwordInput.showPassword
                    }
                }
            }

            RowLayout {
                Layout.fillWidth: true
                Layout.alignment: Qt.AlignRight
                spacing: 15

                Button {
                    text: "Cancelar"
                    Layout.preferredWidth: 100
                    Layout.preferredHeight: 45
                    background: Rectangle { color: "transparent"; border.color: "#8a8d94"; border.width: 2; radius: 8 }
                    contentItem: Text { text: parent.text; color: "#8a8d94"; horizontalAlignment: Text.AlignHCenter; verticalAlignment: Text.AlignVCenter }
                    onClicked: {
                        passwordInput.text = ""
                        passwordPopup.close()
                    }
                }

                Button {
                    text: "Conectar"
                    Layout.preferredWidth: 120
                    Layout.preferredHeight: 45
                    background: Rectangle { color: "#fc724f"; radius: 8 }
                    contentItem: Text { text: parent.text; color: "#0b0d13"; font.bold: true; horizontalAlignment: Text.AlignHCenter; verticalAlignment: Text.AlignVCenter }
                    onClicked: {
                        networkBackend.connect_network(selectedNetwork, passwordInput.text)
                        passwordInput.text = ""
                        passwordPopup.close()
                    }
                }
            }
        }
    }

    // Popup para mostrar errores de conexión
    Popup {
        id: errorPopup
        width: 300; height: 150
        x: Math.round((parent.width - width) / 2)
        y: Math.round((parent.height - height) / 2)
        modal: true
        background: Rectangle { color: "#191723"; radius: 10; border.color: "#ff3333"; border.width: 2 }

        ColumnLayout {
            anchors.fill: parent; anchors.margins: 20; spacing: 10
            Text { text: "Error de Conexión"; color: "#ff3333"; font.bold: true; font.pixelSize: 18; Layout.alignment: Qt.AlignHCenter }
            Text { id: errorTextPopup; text: ""; color: "#FFF"; font.pixelSize: 14; Layout.fillWidth: true; wrapMode: Text.WordWrap; horizontalAlignment: Text.AlignHCenter }
            Button {
                text: "Cerrar"
                Layout.alignment: Qt.AlignHCenter
                background: Rectangle { color: "#331f1f"; radius: 8; border.color: "#501617"; border.width: 2 }
                contentItem: Text { text: parent.text; color: "#ff3333" }
                onClicked: errorPopup.close()
            }
        }
    }
}