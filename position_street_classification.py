import json
import codecs

list_ID0 = []
list_ID1 = []
list_ID2 = []
list_ID3 = []
list_ID4 = []
list_ID5 = []
with open('data.json', 'rb') as json_data:
    data_set = json.loads(json_data.read())
    print(len(data_set), "datas loaded succesfully")
    listSpam = ['24 / 24','24 / 7','1 / 500']
    listNear = ['cách','cạnh','gần','kề'] # danh sách những tính từ đồng nghĩa với gần
    listMT = ['mặt tiền','mặt đường','mặt phố']
    listPlural = ['2','3','hai','ba']
    listSingularSlash = ['1 sẹc','một sẹc','1 /','một /']
    listPluralSlash = ['2 sẹc', 'hai sẹc', '2 /', 'hai /','3 sẹc', 'ba sẹc', '3 /', 'ba /']
    listH = ['hẻm','hẽm'] # em nghĩ có thêm các từ như 'ngõ','kiệt' nhưng không chắc lắm
    for data in data_set:
        position_street = 0
        attribute = data['attributes']

        check_MT_in_content = 0
        check_H_in_content = 0



        H_keyword = 'hẻm hẽm'  # phát sinh từ TEST 3 do không bỏ dấu
        # Trong data em có gặp môt số case có position là 'ngõ'. Em không chắc ngõ hoặc kiệt (cách gọi khác của ngõ)
        # có giống như hẻm không nên không thêm vào keyword

        bagOfWordsH = H_keyword.split(' ')  # túi từ hẽm
        for i in range(0, len(attribute)):
            # - Xét số lượng '/' trong địa chỉ của bài đăng
            # Tuy nhiên có 1 số case như 119342: "addr_street" chỉ bao gồm tên đường, còn địa chỉ thật lại
            # nằm trong "normal" liên trước -> xét thêm attribute['content'] liền trước
            # Bonus case 118317: "normal" chứa địa chỉ nhưng attribute['content'] liền sau không phải type addr_street
            # -> Xét địa chỉ trong toàn bộ addr_street và normal
            # Bonus case 118727: 31/8/2000 là ngày tháng chớ không phải địa chỉ 2 sẹc
            if attribute[i]['type'] == 'addr_street' or attribute[i]['type'] == 'normal':
                # Bởi vì xét cả trong type normal nên cần loại bỏ các content có nội dung như 'giá chỉ còn 1/3...'
                # 'liên hệ 24/7',... -> Điểm chung của những content này là có nội dung khá dài
                if attribute[i]['type'] == 'normal' and len(attribute[i]['content']) > 50:
                    continue
                # Check spam
                checkSpam = 0
                for keyword in listSpam:
                    if keyword in attribute[i]['content']:
                        checkSpam = 1
                        break
                if checkSpam == 1:
                    continue
                #Count slash
                num_slash = 0
                index_of_slash = -1
                while True:
                    index_of_slash = attribute[i]['content'].find('/', index_of_slash + 1)
                    if index_of_slash == -1:
                        break
                    if index_of_slash - 2 >= 0 and index_of_slash + 2 < len(attribute[i]['content']):
                        if attribute[i]['content'][index_of_slash - 2].isdecimal() and attribute[i]['content'][
                            index_of_slash + 2].isdecimal():
                            if len(attribute[i]['content'][index_of_slash + 2:len(attribute[i]['content'])].split()[
                                       0]) > 2:
                                # Nếu gặp phải các case như 31 / 08 / 2000
                                # hoặc 012345678 / 87654321 thì không tính là sẹc của đưởng
                                # Em chọn bỏ đi các tình huống có len > 2 vì thường sau / ít khi có số trên 3 chữ số
                                num_slash = 0
                                continue
                            num_slash += 1
                if num_slash > 1:
                    position_street = 4  # Hẻm từ 2 sẹc trở lên
                    break
                elif num_slash == 1:
                    position_street = 3  # Hẻm/Hẻm 1 sẹc
                    break
                else:  # Địa chỉ cụ thể mà k sẹc là nhà mặt tiền
                    if attribute[i]['type'] == 'addr_street':
                        if i != 0 and attribute[i - 1]['type'] == 'normal' and attribute[i - 1]['content'] != '\n':
                            if attribute[i - 1]['content'].split()[-1].isdecimal():
                                position_street = 1
                                break
            # Xét nội dung của position xem có chữ cái keyword nhận diện hay không
            # cụm từ "mặt tiền" được phân loại khá lộn xộn trong type của attribute, có cả trong normal và position (đa số)
            # ví dụ cụm từ 'mặt tiền' trong case 118408
            if attribute[i]['type'] == 'position' or attribute[i]['type'] == 'normal':
                # 1 số case có type normal có content như sau: 'cách mặt tiền...', 'cạnh hẽm...','gần...','kề...'
                # -> Không xét những case này là có MT/H
                norm_pos_content = attribute[i]['content'].lower()
                checkNear = 0
                for keyword in listNear:
                    if keyword in norm_pos_content:
                        checkNear = 1
                        break
                if checkNear == 1:
                    continue

                bagOfWordsText = norm_pos_content.split(' ')  # túi từ nội dung
                check_MT_in_position = 0
                if 'mt' in bagOfWordsText:
                    check_MT_in_position = 1
                else:
                    for keyword in listMT:
                        if keyword in norm_pos_content:
                            check_MT_in_position = 1
                            break
                # Tìm kiếm keyword về MT trong content
                if check_MT_in_position == 1:
                    if i != 0 and attribute[i - 1]['type'] == 'normal' and attribute[i - 1]['content'] != '\n':
                        # Tại sao cần có điều kiện này ?
                        # Trong data có tình huống là '160 m 2 mt' -> số 2 trong m2 la diện tích, k phải là số lượng mt
                        # Ngoài ra trong case 119735 có tình huống 'Quận 3 mặt tiền ...' -> số 3 là Quận, k phải là số lượng
                        # -> Nên em chỉ xét attribute liền trước nếu là normal để phân biệt với area và district
                        # Để tìm kiếm cụm từ chỉ số lượng nhiều như '2,3,hai,ba' trong tình huống này, em cảm thấy cách tìm
                        # kiếm những từ trên trong cụm liền trước cũng ổn nhưng không cần thiết lắm vì cụm từ '2 mt' luôn
                        # đi chung với nhau nên chỉ xét phần tử cuối cùng của attribute['content'] liền trước là được
                        word_before_MT = attribute[i - 1]['content'].split()[-1]
                        # normalize word_before_MT
                        word_before_MT = word_before_MT.lower()
                        if word_before_MT in listPlural:
                            position_street = 2  # Nhà 2/3 MT
                            break
                    check_MT_in_content = 1
                    continue  # Nếu như có MT thì không cần check hẽm
                # Tìm kiếm keyword về hẽm trong content
                check_H_in_position = 0
                for keyword in listH:
                    if keyword in norm_pos_content:
                        check_H_in_position = 1
                        break
                if check_H_in_position == 1:
                    if i != len(attribute) - 1:
                        # kiểm tra xem phía sau có '1/2/3 sẹc' không
                        # Xử lý tương tự như mặt tiền, lần này ta xét 2 từ đầu tiên của attribute['content'] liền sau
                        # Nhưng vì lần này cụm từ ta xét là '1 sec', '2 sec', '3 sec' đều là những cụm từ không bị nhầm lẫn
                        # với các cụm từ khác trong tiếng Việt cộng thêm việc attribute['content'] có độ dài không quá lớn
                        # nên có thể sử dụng method find() thay cho túi từ
                        word_after_hem = attribute[i + 1]['content'].lower()
                        Outloop = 0
                        for word in listSingularSlash:
                            if word in word_after_hem:
                                position_street = 3  # Hẽm 1 sẹc
                                Outloop = 1
                                break
                        if Outloop == 1:
                            break
                        for word in listPluralSlash:
                            if word in word_after_hem:
                                position_street = 4  # Hẽm nhiều hơn sẹc
                                Outloop = 1
                                break
                        if Outloop == 1:
                            break
                    check_H_in_content = 1  # Chưa kết luận là nhà hẽm 1 sẹc vội, có khả năng được nhắc đến ở sau

        if check_MT_in_content == 1 and check_H_in_content == 1:
            position_street = 5  # vừa có mặt tiền vừa có hẽm nên khả năng cao là 2 mặt tiền hẽm
        if position_street == 0:  # Nếu chưa kết luận position_street
            if check_H_in_content == 1 and check_MT_in_content == 0:
                position_street = 3  # có chứa keyword hẽm nhưng không đề cập mấy sẹc -> phân loại Hẽm/Hẽm 1 sẹc
            elif check_MT_in_content == 1 and check_H_in_content == 0:
                position_street = 1  # có chứa keyword MT nhưng không đề cập số lượng -> phân loại MT

        # Classify result into list
        if position_street == 1:
            list_ID1.append(data['id'])
        elif position_street == 2:
            list_ID2.append(data['id'])
        elif position_street == 3:
            list_ID3.append(data['id'])
        elif position_street == 4:
            list_ID4.append(data['id'])
        elif position_street == 5:
            list_ID5.append(data['id'])
        else:
            list_ID0.append(data['id'])
    with codecs.open('result2.json', 'a') as reader:
        json.dump('ListID1:' , reader, indent = 2, sort_keys=True)
        json.dump(len(list_ID1), reader, indent=2, sort_keys=True)
        json.dump(list_ID1, reader, indent=2, sort_keys=True)
        json.dump('ListID2:', reader, indent=2, sort_keys=True)
        json.dump(len(list_ID2), reader, indent=2, sort_keys=True)
        json.dump(list_ID2, reader, indent=2, sort_keys=True)
        json.dump('ListID4:', reader, indent=2, sort_keys=True)
        json.dump(len(list_ID4), reader, indent=2, sort_keys=True)
        json.dump(list_ID4, reader, indent=2, sort_keys=True)

        json.dump('ListID0:', reader, indent=2, sort_keys=True)
        json.dump(len(list_ID0), reader, indent=2, sort_keys=True)
        json.dump(list_ID0, reader, indent=2, sort_keys=True)
        json.dump('ListID3:', reader, indent=2, sort_keys=True)
        json.dump(len(list_ID3), reader, indent=2, sort_keys=True)
        json.dump(list_ID3, reader, indent=2, sort_keys=True)
        json.dump('ListID5:', reader, indent=2, sort_keys=True)
        json.dump(len(list_ID5), reader, indent=2, sort_keys=True)
        json.dump(list_ID5, reader, indent=2, sort_keys=True)
    print('Done')