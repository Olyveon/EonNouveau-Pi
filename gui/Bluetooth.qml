import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Item {
    id: bluetoothRoot

    // Keep raw device data here — source of truth
    property var deviceMap: ({})

    ListModel {
        id: deviceModel
    }

    function statusPriority(status) {
        switch (status) {
            case "connected": return 0
            case "paired":    return 1
            default:          return 2  // "scanned"
        }
    }

    function rebuildModel() {
        var devices = Object.values(deviceMap)
        devices.sort(function(a, b) {
            var pa = statusPriority(a.status)
            var pb = statusPriority(b.status)
            if (pa !== pb) return pa - pb
            // Optional secondary sort: strongest signal first within same status
            return b.rssi - a.rssi
        })
        deviceModel.clear()
        for (var i = 0; i < devices.length; i++) {
            deviceModel.append(devices[i])
        }
    }

    Layout.fillWidth: true
    Layout.fillHeight: true

    Component.onCompleted: {
        // Al cargar la pestaña, pedimos a Python que busque los dispositivos
        deviceMap = {}
        deviceModel.clear()
        bluetoothBackend.start_scan()
    }

    Connections {
        target: bluetoothBackend

        function onPairing_finished(mac, status) {
        if (deviceMap[mac]) {
            deviceMap[mac].status = status === "paired" ? "paired" : "scanned"
            rebuildModel()
            }
        }
        

        function onConnection_changed(mac, status) {
            if (deviceMap[mac]) {
                deviceMap[mac].status = status === "connected" ? "connected"
                                    : (deviceMap[mac].status === "connected" ? "paired" : deviceMap[mac].status)
                rebuildModel()
            }
        }

        function onDevice_found(jsonStr) {
            var d = JSON.parse(jsonStr)
            deviceMap[d.mac] = d
            rebuildModel()
        }

        function onDevices_ready(jsonStr) {
            //console.log("Scan finished:", jsonStr)
        }

        function onScan_error(msg) {
            console.log("Bluetooth scan error:", msg)
        }
    }

    // On new scan:
    function startScan() {
        deviceMap = {}
        deviceModel.clear()
        bluetoothBackend.start_scan()
    }

    ColumnLayout {
        anchors.fill: parent 
        spacing: 20


        RowLayout {
            Layout.fillWidth: true
            Layout.topMargin: 10
            
            Text {
                text: "Dispositivos Disponibles"
                color: "#FFFFFF"
                font.pixelSize: 22
                font.bold: true
                Layout.fillWidth: true
            }

            Button {
                text: "↻ Refrescar"
                background: Rectangle { color: "transparent" }
                contentItem: Text { text: parent.text; color: "#fc724f"; font.pixelSize: 16 }
                onClicked: startScan()
            }
        }

        // Available Devices List
        Rectangle {
            Layout.fillWidth: true
            Layout.fillHeight: true
            color: "transparent"

            ListView {
                id: devicesList
                anchors.fill: parent
                clip: true
                spacing: 12
                ScrollBar.vertical: ScrollBar { policy: ScrollBar.AlwaysOff }

                model: deviceModel 

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
                            
                            if (model.status == "paired") {
                                // Si esta emparejado, tratar de conectarse
                                print(model.mac)
                                bluetoothBackend.connect_device(model.mac)
                            } else if (model.status == "connected") {
                                // Si esta conectado se desconecta
                                bluetoothBackend.disconnect_device(model.mac)
                                
                            } else if (model.status == "scanned"){
                                // Si no esta emparajeado, tratar de emparejarse
                                bluetoothBackend.pair_device(model.mac)
                            }
                        }
                    }

                    RowLayout {
                        anchors.fill: parent
                        anchors.margins: 15
                        spacing: 15

                        ColumnLayout {
                            spacing: 2
                            Label {
                                text: model.name
                                font.bold: true
                                color: "white"
                            }
                            Label {
                                text: model.mac 
                                font.pixelSize: 11
                                color: "white"
                                opacity: 0.6
                            }
                        }

                        Item { Layout.fillWidth: true }

                        Label {
                            text: model.status === "connected" ? "Conectado"
                                : model.status === "paired" ? "Emparejado"
                                : "Detectado"
                            color: model.status === "connected" ? "green"
                                : model.status === "paired" ? "orange"
                                :"gray"
                        }
                        

                        
                        
                        Button {
                            id: connectBtn
                            text: model.status === "scanned" ? "Emparejar" : "Olvidar"
                            background: Rectangle { 
                                color: "#191723"
                                radius: 5 
                                border.color: model.status === "scanned" ? "#fc724f" : "#8a8d94" 
                                border.width: 1.1 
                            }
                            contentItem: Text { 
                                text: connectBtn.text
                                color: model.status === "scanned" ? "#fc724f" : "#8a8d94" 
                                horizontalAlignment: Text.AlignHCenter 
                                verticalAlignment: Text.AlignVCenter 
                            }
                            Layout.preferredWidth: 90
                            Layout.preferredHeight: 35
                            onClicked: {
                                if (model.status == "scanned") {
                                    // Si no esta emparajeado, tratar de emparejarse
                                    bluetoothBackend.pair_device(model.mac)
                                } else {
                                    // Si esta conectado o emperajedo se olvida
                                    bluetoothBackend.forget_device(model.mac) 
                                }
                            }
                        }
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